const fs = require('fs');
const path = require('path');

// Template for the HTML dashboard
const template = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seattle Dinner Finder - {{DATE}}</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            margin-bottom: 2rem;
            color: white;
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        .restaurant-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .restaurant-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        .restaurant-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.75rem;
        }
        .restaurant-name {
            font-size: 1.4rem;
            font-weight: 700;
            color: #1a1a2e;
        }
        .neighborhood-badge {
            background: #e0e7ff;
            color: #4338ca;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .cuisine-type {
            color: #666;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        .vibe-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 0.75rem;
        }
        .vibe-tag {
            background: #fef3c7;
            color: #92400e;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .details {
            display: flex;
            gap: 1.5rem;
            font-size: 0.9rem;
            color: #555;
            margin-bottom: 0.75rem;
            flex-wrap: wrap;
        }
        .detail-item {
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }
        .reservation-status {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            text-decoration: none;
            margin-right: 0.5rem;
        }
        .available {
            background: #10b981;
            color: white;
        }
        .limited {
            background: #f59e0b;
            color: white;
        }
        .description {
            margin-top: 0.75rem;
            font-size: 0.9rem;
            color: #666;
            line-height: 1.5;
        }
        .footer {
            text-align: center;
            margin-top: 2rem;
            color: rgba(255,255,255,0.8);
            font-size: 0.85rem;
        }
        .why-fun {
            background: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 0.75rem 1rem;
            margin-top: 0.75rem;
            border-radius: 0 8px 8px 0;
            font-size: 0.9rem;
            color: #166534;
        }
        .why-fun strong {
            display: block;
            margin-bottom: 0.25rem;
        }
        .reservation-link {
            color: #4338ca;
            text-decoration: none;
            font-weight: 600;
        }
        .reservation-link:hover {
            text-decoration: underline;
        }
        .archive-link {
            display: inline-block;
            margin-top: 1rem;
            color: white;
            text-decoration: none;
            opacity: 0.8;
        }
        .archive-link:hover {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🍽️ Seattle Dinner Finder</h1>
            <p class="subtitle">{{DAY_OF_WEEK}}, {{DATE_DISPLAY}} · 2 people · ~7:00 PM</p>
        </header>
        
        {{RESTAURANT_CARDS}}
        
        <div class="footer">
            <p>Researched for north Seattle: Ballard, Fremont, Green Lake, Queen Anne</p>
            <p>Updated daily at 9:00 AM PT · Call restaurants to confirm availability</p>
            <a href="./archive.html" class="archive-link">📅 View Past Recommendations</a>
        </div>
    </div>
</body>
</html>`;

function formatDate(date) {
    const options = { month: 'long', day: 'numeric', year: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

function formatDayOfWeek(date) {
    return date.toLocaleDateString('en-US', { weekday: 'long' });
}

function generateRestaurantCard(restaurant) {
    return `
        <div class="restaurant-card">
            <div class="restaurant-header">
                <div class="restaurant-name">${restaurant.name}</div>
                <span class="neighborhood-badge">${restaurant.neighborhood}</span>
            </div>
            <div class="cuisine-type">${restaurant.cuisine} · ${restaurant.price}</div>
            <div class="vibe-tags">
                ${restaurant.vibes.map(vibe => `<span class="vibe-tag">${vibe}</span>`).join('')}
            </div>
            <div class="details">
                <span class="detail-item">📍 ${restaurant.address}</span>
                <span class="detail-item">📞 ${restaurant.phone}</span>
            </div>
            <a href="${restaurant.reservationUrl}" class="reservation-status ${restaurant.availability}" target="_blank">
                ${restaurant.availability === 'available' ? '✓ Check Availability' : '⚠ Limited Availability'}
            </a>
            <div class="why-fun">
                <strong>Why it's fun:</strong> ${restaurant.whyFun}
            </div>
        </div>
    `;
}

function build() {
    const today = new Date();
    const dateStr = today.toISOString().split('T')[0];
    
    // Load restaurant data
    const dataPath = path.join(__dirname, '..', 'data', `${dateStr}.json`);
    let restaurants = [];
    
    if (fs.existsSync(dataPath)) {
        restaurants = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
    } else {
        // Fallback to sample data if no research data exists yet
        restaurants = getSampleData();
    }
    
    // Generate restaurant cards
    const cardsHtml = restaurants.map(generateRestaurantCard).join('\n');
    
    // Fill template
    let html = template
        .replace('{{DATE}}', dateStr)
        .replace('{{DATE_DISPLAY}}', formatDate(today))
        .replace('{{DAY_OF_WEEK}}', formatDayOfWeek(today))
        .replace('{{RESTAURANT_CARDS}}', cardsHtml);
    
    // Ensure dist directory exists
    const distPath = path.join(__dirname, '..', 'dist');
    if (!fs.existsSync(distPath)) {
        fs.mkdirSync(distPath, { recursive: true });
    }
    
    // Write index.html
    fs.writeFileSync(path.join(distPath, 'index.html'), html);
    
    // Generate archive page
    generateArchivePage(distPath);
    
    console.log(`✅ Built site for ${dateStr}`);
}

function generateArchivePage(distPath) {
    const dataDir = path.join(__dirname, '..', 'data');
    const files = fs.readdirSync(dataDir)
        .filter(f => f.endsWith('.json'))
        .sort()
        .reverse();
    
    const archiveHtml = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Seattle Dinner Finder - Archive</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 2rem;
            color: white;
        }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 2rem; }
        .date-list { list-style: none; }
        .date-item {
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            backdrop-filter: blur(10px);
        }
        .date-item a {
            color: white;
            text-decoration: none;
            font-size: 1.1rem;
        }
        .date-item a:hover { text-decoration: underline; }
        .back-link {
            display: inline-block;
            margin-top: 2rem;
            color: white;
            text-decoration: none;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📅 Past Recommendations</h1>
        <ul class="date-list">
            ${files.map(f => {
                const date = f.replace('.json', '');
                const display = new Date(date).toLocaleDateString('en-US', { 
                    weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' 
                });
                return `<li class="date-item"><a href="./${date}.html">${display}</a></li>`;
            }).join('')}
        </ul>
        <a href="./index.html" class="back-link">← Back to today's picks</a>
    </div>
</body>
</html>`;
    
    fs.writeFileSync(path.join(distPath, 'archive.html'), archiveHtml);
}

function getSampleData() {
    return [
        {
            name: "Revel",
            neighborhood: "Fremont",
            cuisine: "Korean Fusion",
            price: "$$",
            vibes: ["🎉 Lively", "🔥 Open Kitchen", "🍜 Shareable"],
            address: "401 N 36th St",
            phone: "(206) 547-2040",
            reservationUrl: "https://www.opentable.com/r/revel-seattle",
            availability: "available",
            whyFun: "A quintessential Seattle spot with a massive open kitchen. Chef Rachel Yang's creative Korean comfort food is perfect for sharing, and the energy is always buzzing."
        },
        {
            name: "The Ballard Cut",
            neighborhood: "Ballard",
            cuisine: "Steakhouse",
            price: "$$$",
            vibes: ["🥃 Whiskey Bar", "🥩 Steakhouse", "✨ Upscale"],
            address: "2221 NW Market St",
            phone: "(206) 829-8963",
            reservationUrl: "https://www.opentable.com/r/the-ballard-cut-seattle",
            availability: "available",
            whyFun: "Farm-to-table steakhouse with an incredible Japanese whiskey selection. The atmosphere strikes that perfect balance between special-occasion nice and comfortably casual."
        },
        {
            name: "Grappa",
            neighborhood: "Queen Anne",
            cuisine: "Italian",
            price: "$$",
            vibes: ["🍝 Handmade Pasta", "🍷 Wine Bar", "💕 Romantic"],
            address: "2 W Boston St",
            phone: "(206) 323-8881",
            reservationUrl: "https://www.opentable.com/r/grappa-seattle",
            availability: "available",
            whyFun: "Upper Queen Anne's hidden gem with fresh handmade pasta and an extensive grappa and wine list. The intimate atmosphere is perfect for date night."
        }
    ];
}

// Run build
build();
