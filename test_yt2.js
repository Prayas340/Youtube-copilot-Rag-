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

function parseXmlCaptions(xml) {
    const items = [];
    const regex = /<text start="([\d.]+)"[^>]*>(.*?)<\/text>/g;
    let match;
    while ((match = regex.exec(xml)) !== null) {
        const start = parseFloat(match[1]);
        const text = match[2].replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&#39;/g, "'").replace(/&quot;/g, '"').replace(/<[^>]+>/g, '').trim();
        const mins = Math.floor(start / 60);
        const secs = Math.floor(start % 60);
        const formatted_time = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        items.append || items.push({
            start: Math.floor(start),
            formatted_time,
            text
        });
    }
    return items;
}

async function getFullData(videoId) {
    try {
        const oembedJson = await fetchUrl(`https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`);
        const oembed = JSON.parse(oembedJson);

        const html = await fetchUrl(`https://www.youtube.com/watch?v=${videoId}`);
        const match = html.match(/ytInitialPlayerResponse\s*=\s*({.+?});/);
        
        let title = oembed.title || '';
        let channel = oembed.author_name || '';
        let description = '';
        let captions = [];

        if (match) {
            const playerResponse = JSON.parse(match[1]);
            if (playerResponse.videoDetails) {
                title = playerResponse.videoDetails.title || title;
                channel = playerResponse.videoDetails.author || channel;
                description = playerResponse.videoDetails.shortDescription || '';
            }
            const captionTracks = playerResponse.captions?.playerCaptionsTracklistRenderer?.captionTracks || [];
            if (captionTracks.length > 0) {
                const xml = await fetchUrl(captionTracks[0].baseUrl);
                captions = parseXmlCaptions(xml);
            }
        }

        console.log("RESULT:", {
            title,
            channel,
            descLength: description.length,
            captionCount: captions.length,
            sampleCaption: captions[0]
        });
    } catch (e) {
        console.error("Fetch Error:", e.message);
    }
}

getFullData("L_Guz73e6fw");
