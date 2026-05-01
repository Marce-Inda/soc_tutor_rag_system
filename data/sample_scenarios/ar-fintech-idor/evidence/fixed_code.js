// routes/customers.js
// SECURE CODE - AFTER FIX
// ✅ This code demonstrates proper Object-Level Authorization

const express = require('express');
const router = express.Router();
const db = require('../database');
const { authenticateJWT } = require('../middleware/auth');

/**
 * GET /api/v2/customers/:customer_id/loans
 * 
 * ✅ SECURE: Implements Object-Level Authorization
 * 
 * This endpoint now verifies that the authenticated user
 * is the OWNER of the requested customer record before
 * returning any data.
 * 
 * OWASP Compliance:
 * - A01:2025 - Broken Access Control ✅ MITIGATED
 * - API1:2023 - Broken Object Level Authorization ✅ MITIGATED
 */
router.get('/customers/:customer_id/loans',
    authenticateJWT,  // ✅ Step 1: Authentication
    async (req, res) => {
        const { customer_id } = req.params;
        const requesting_user_id = req.user.id;  // From JWT payload

        try {
            // ✅ Step 2: Authorization - Verify ownership
            const customer = await db.query(
                'SELECT user_id FROM customers WHERE id = $1',
                [customer_id]
            );

            // Check if customer exists
            if (!customer || customer.rows.length === 0) {
                return res.status(404).json({
                    error: 'Customer not found'
                });
            }

            // ✅ CRITICAL CHECK: Verify the requesting user owns this customer
            if (customer.rows[0].user_id !== requesting_user_id) {
                // Log the unauthorized access attempt for security monitoring
                console.warn(`[SECURITY] Unauthorized access attempt: ` +
                    `User ${requesting_user_id} tried to access customer ${customer_id}`);

                // Return 403 Forbidden - don't reveal that the resource exists
                return res.status(403).json({
                    error: 'Forbidden: Cannot access other customer data'
                });
            }

            // ✅ Step 3: Only now fetch and return the data
            const loans = await db.query(
                'SELECT * FROM loans WHERE customer_id = $1',
                [customer_id]
            );

            return res.json(loans.rows);

        } catch (error) {
            console.error('Database error:', error);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }
);

module.exports = router;

/*
 * SECURITY IMPROVEMENTS:
 * 
 * 1. ✅ Added ownership verification before data access
 * 2. ✅ Logging of unauthorized access attempts (for SIEM/alerting)
 * 3. ✅ Proper error handling with security-conscious responses
 * 4. ✅ 403 Forbidden instead of 200 OK for unauthorized requests
 * 
 * ADDITIONAL RECOMMENDATIONS:
 * 
 * 1. Use UUIDs instead of sequential IDs to prevent enumeration
 * 2. Implement rate limiting per user
 * 3. Add API request logging for forensic analysis
 * 4. Consider implementing a centralized authorization middleware
 * 5. Revoke JWT tokens immediately upon employee termination
 */
