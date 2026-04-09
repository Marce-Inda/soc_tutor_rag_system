// routes/customers.js
// VULNERABLE CODE - BEFORE FIX
// ⚠️ This code is intentionally insecure for educational purposes

const express = require('express');
const router = express.Router();
const db = require('../database');
const { authenticateJWT } = require('../middleware/auth');

/**
 * GET /api/v2/customers/:customer_id/loans
 * 
 * ❌ VULNERABILITY: Insecure Direct Object Reference (IDOR)
 * 
 * This endpoint has AUTHENTICATION (JWT required) but NO AUTHORIZATION
 * (no check that the requesting user owns this customer_id).
 * 
 * Any authenticated user can access ANY customer's loan data by simply
 * changing the customer_id in the URL.
 * 
 * OWASP Classification:
 * - A01:2025 - Broken Access Control
 * - API1:2023 - Broken Object Level Authorization (BOLA)
 */
router.get('/customers/:customer_id/loans',
    authenticateJWT,  // ✅ Authentication: User must have valid JWT
    async (req, res) => {
        const { customer_id } = req.params;

        // ❌ NO AUTHORIZATION CHECK HERE!
        // We never verify that the authenticated user has permission
        // to access this specific customer's data

        try {
            const loans = await db.query(
                'SELECT * FROM loans WHERE customer_id = $1',
                [customer_id]
            );

            // ❌ Returns data without checking ownership
            return res.json(loans);

        } catch (error) {
            console.error('Database error:', error);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }
);

module.exports = router;

/*
 * ATTACK SCENARIO:
 * 
 * 1. Attacker obtains a valid JWT (stolen, leaked, or from compromised account)
 * 2. Attacker makes requests to /api/v2/customers/1001/loans
 * 3. Server validates JWT ✅ (authentication passes)
 * 4. Server returns customer 1001's loan data ❌ (no authorization check)
 * 5. Attacker enumerates: /customers/1002/loans, /customers/1003/loans, etc.
 * 6. All requests return 200 OK with sensitive data
 * 
 * RESULT: Mass data exfiltration via sequential enumeration
 */
