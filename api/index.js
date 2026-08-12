module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    res.setHeader('Content-Type', 'application/json');
    res.status(200).end(JSON.stringify({ status: 'ok', message: 'YouTube Copilot API Engine Live' }));
};
