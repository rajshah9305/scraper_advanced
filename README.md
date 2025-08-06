# Elite Web Scraper

A powerful, elite-level web scraping tool designed to extract data from any website with advanced anti-detection capabilities and the ability to bypass robots.txt restrictions.

## Features

- **Advanced Anti-Detection**: Randomized user agents, headers, and request delays
- **Proxy Support**: Rotate through proxy lists to avoid IP bans
- **JavaScript Rendering**: Selenium integration for dynamic content
- **Robots.txt Bypass**: Option to ignore robots.txt restrictions
- **Comprehensive Data Extraction**: Extract titles, meta descriptions, headings, paragraphs, links, and images
- **Robust Error Handling**: Detailed logging and graceful error recovery
- **Multiple Output Formats**: Save data as JSON with structured format
- **Web Interface**: Flask-based web application with real-time progress updates
- **Batch Processing**: Scrape multiple URLs efficiently

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/elite-web-scraper.git
cd elite-web-scraper
```

2. Install required dependencies:

### For Basic Usage
```bash
pip install -r requirements.txt
```

### For Web Interface
```bash
pip install -r flask_requirements.txt
```

### Additional Requirements for Selenium

If you plan to use Selenium for JavaScript-heavy websites, you'll need to install Chrome/Chromium:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser

# macOS
brew install --cask google-chrome

# Windows
# Download and install Chrome from https://www.google.com/chrome/
```

## Quick Start

### Basic Usage

```python
from advanced_scraper import AdvancedWebScraper

# Initialize scraper
scraper = AdvancedWebScraper()

# Scrape a single URL
data = scraper.scrape("https://example.com")

# Save data
if data:
    scraper.save_data([data], "output.json")

# Clean up
scraper.close()
```

### Advanced Configuration

```python
from advanced_scraper import AdvancedWebScraper

# Configure with all features
proxy_list = [
    "http://proxy1:port",
    "http://proxy2:port",
]

scraper = AdvancedWebScraper(
    use_proxies=True,           # Enable proxy rotation
    proxy_list=proxy_list,      # List of proxies
    ignore_robots=True,         # Bypass robots.txt
    use_selenium=True           # Enable JavaScript rendering
)

# Scrape multiple URLs
urls = [
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
]

results = scraper.scrape_multiple(urls)
scraper.save_data(results, "scraped_data.json")
scraper.close()
```

### Web Interface

Start the Flask web application:

```bash
python flask_scraper_app.py
```

Then open your browser to `http://localhost:5000` to access the web interface.

## Configuration Options

### AdvancedWebScraper Parameters

- `use_proxies` (bool): Enable proxy rotation (default: False)
- `proxy_list` (list): List of proxy URLs (default: [])
- `ignore_robots` (bool): Bypass robots.txt restrictions (default: True)
- `use_selenium` (bool): Use Selenium for JavaScript rendering (default: False)

### Proxy Format

Proxies should be provided as a list of strings in the format:
```python
proxy_list = [
    "http://username:password@proxy1:port",
    "https://proxy2:port",
    "socks5://proxy3:port"
]
```

## Output Format

The scraper returns structured data in the following format:

```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "meta_description": "Page meta description",
  "headings": [
    {
      "level": 1,
      "text": "Main Heading"
    },
    {
      "level": 2,
      "text": "Sub Heading"
    }
  ],
  "paragraphs": [
    "First paragraph text...",
    "Second paragraph text..."
  ],
  "links": [
    {
      "url": "https://link1.com",
      "text": "Link Text"
    }
  ],
  "images": [
    {
      "src": "https://example.com/image.jpg",
      "alt": "Image description"
    }
  ]
}
```

## Examples

See `examples.py` for comprehensive usage examples including:
- Basic web scraping
- JavaScript-heavy website scraping
- Multiple URL processing
- Proxy usage
- Ethical scraping practices
- Custom data extraction

## Ethical Considerations and Legal Disclaimer

### Robots.txt Bypass

This scraper includes the ability to bypass robots.txt restrictions. While this provides powerful scraping capabilities, it's important to understand the ethical and legal implications:

**Ethical Guidelines:**
- Always respect website terms of service
- Don't overload servers with excessive requests
- Consider the impact on website performance
- Respect copyright and intellectual property rights
- Use scraped data responsibly

**Legal Considerations:**
- Bypassing robots.txt may violate website terms of service
- Some jurisdictions have laws against unauthorized data access
- Commercial use of scraped data may have additional legal implications
- Always consult with legal counsel for commercial applications

**Best Practices:**
- Use reasonable delays between requests
- Limit concurrent requests
- Consider reaching out to website owners for permission
- Respect rate limits and server capacity
- Monitor your scraping impact

### Recommended Ethical Usage

1. **Start with robots.txt compliance**: Set `ignore_robots=False` initially
2. **Use appropriate delays**: Don't overwhelm servers
3. **Respect rate limits**: Implement reasonable request frequencies
4. **Monitor server response**: Watch for 429 (Too Many Requests) responses
5. **Consider alternatives**: Check if APIs or data feeds are available

## Troubleshooting

### Common Issues

**Chrome/Chromium not found:**
```
selenium.common.exceptions.WebDriverException: Message: 'chromedriver' executable needs to be in PATH
```
Solution: Install Chrome/Chromium as described in the installation section.

**Proxy connection errors:**
```
requests.exceptions.ProxyError: HTTPSConnectionPool
```
Solution: Verify proxy credentials and connectivity. Remove non-working proxies from the list.

**Memory issues with Selenium:**
```
selenium.common.exceptions.WebDriverException: Message: unknown error: Chrome failed to start
```
Solution: Ensure sufficient system memory. Consider using headless mode (already enabled by default).

### Performance Tips

1. **Use proxies wisely**: Too many proxy switches can slow down scraping
2. **Optimize delays**: Balance between speed and detection avoidance
3. **Batch processing**: Process URLs in batches rather than one by one
4. **Resource cleanup**: Always call `scraper.close()` to free resources

## Project Structure

```
elite-web-scraper/
├── README.md                 # This file
├── requirements.txt          # Basic dependencies
├── flask_requirements.txt    # Web interface dependencies
├── advanced_scraper.py      # Main scraper class
├── scraper.py               # Simple scraper implementation
├── examples.py              # Usage examples
├── flask_scraper_app.py     # Flask web application
├── setup_script.py          # Setup and configuration script
├── templates/
│   └── index.html          # Web interface template
├── uploads/                 # File upload directory
└── results/                 # Scraping results directory
```

## Contributing

This scraper is designed to be modular and extensible. Feel free to:

- Add new extraction methods
- Improve anti-detection techniques
- Add support for new proxy types
- Enhance error handling
- Improve the web interface

## License

This tool is provided for educational and research purposes. Users are responsible for ensuring their usage complies with applicable laws and website terms of service.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration options
3. Ensure all dependencies are properly installed
4. Test with simple websites first before complex ones
5. Open an issue on GitHub for bugs or feature requests 