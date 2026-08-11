const https = require('https');

function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' } }, (res) => {
            let body = '';
            res.on('data', chunk => body += chunk);
            res.on('end', () => resolve(body));
        }).on('error', reject);
    });
}

async function testFetch(videoId) {
    try {
        const html = await fetchUrl(`https://www.youtube.com/watch?v=${videoId}`);
        const match = html.match(/ytInitialPlayerResponse\s*=\s*({.+?});/);
        if (match) {
            const playerResponse = JSON.parse(match[1]);
            const title = playerResponse.videoDetails ? playerResponse.videoDetails.title : '';
            const author = playerResponse.videoDetails ? playerResponse.videoDetails.author : '';
            const description = playerResponse.videoDetails ? playerResponse.videoDetails.shortDescription : '';
            const captionTracks = playerResponse.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
            
            console.log("SUCCESS!");
            console.log("Title:", title);
            console.log("Author:", author);
            console.log("Description length:", description.length);
            console.log("Caption tracks found:", captionTracks.length);

            if (captionTracks.length > 0) {
                const captionUrl = captionTracks[0].baseUrl;
                const xml = await fetchUrl(captionUrl);
                console.log("Xml length:", xml.length);
            }
        } else {
            console.log("ytInitialPlayerResponse not found in HTML");
        }
    } catch (e) {
        console.error("Error:", e.message);
    }
}

testFetch("L_Guz73e6fw");
