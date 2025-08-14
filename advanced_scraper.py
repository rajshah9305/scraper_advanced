import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging
import hashlib
import urllib.parse
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from fake_useragent import UserAgent
    HAS_FAKE_USERAGENT = True
except ImportError:
    HAS_FAKE_USERAGENT = False
    logger.warning("fake-useragent not available, using default user agents")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False
    logger.warning("Selenium not available, disabling JavaScript rendering")

try:
    from urllib.robotparser import RobotFileParser
    HAS_ROBOTPARSER = True
except ImportError:
    HAS_ROBOTPARSER = False
    logger.warning("robotparser not available, robots.txt checking disabled")

@dataclass
class ProxyInfo:
    url: str
    health: int = 100
    response_time: float = 0.0
    last_used: float = 0.0
    success_count: int = 0
    failure_count: int = 0

class RetryManager:
    """Enhanced retry logic with exponential backoff and jitter"""
    
    def __init__(self, max_retries=3, base_delay=1):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def retry_with_backoff(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                
                # Exponential backoff with jitter
                delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                logger.warning(f"Retry {attempt + 1}/{self.max_retries} after {delay:.2f}s")

class ProxyManager:
    """Advanced proxy management with health monitoring"""
    
    def __init__(self, proxy_list: List[str]):
        self.proxies = [ProxyInfo(url=proxy) for proxy in proxy_list]
        self.last_health_check = time.time()
        self.health_check_interval = 300  # 5 minutes
    
    def get_best_proxy(self) -> Optional[str]:
        """Get the healthiest proxy with lowest response time"""
        current_time = time.time()
        
        # Filter healthy proxies
        healthy_proxies = [p for p in self.proxies if p.health > 50]
        
        if not healthy_proxies:
            # If no healthy proxies, use any available
            available_proxies = [p for p in self.proxies if p.health > 0]
            if not available_proxies:
                return None
            healthy_proxies = available_proxies
        
        # Return proxy with best performance
        best_proxy = min(healthy_proxies, 
                        key=lambda x: (x.response_time, -x.health, x.last_used))
        best_proxy.last_used = current_time
        return best_proxy.url
    
    def update_proxy_performance(self, proxy_url: str, success: bool, response_time: float):
        """Update proxy performance metrics"""
        for proxy in self.proxies:
            if proxy.url == proxy_url:
                if success:
                    proxy.health = min(100, proxy.health + 5)
                    proxy.success_count += 1
                    proxy.response_time = response_time
                else:
                    proxy.health = max(0, proxy.health - 20)
                    proxy.failure_count += 1
                break

class AdaptiveRateLimiter:
    """Intelligent rate limiting based on server responses"""
    
    def __init__(self, base_delay=1.0):
        self.base_delay = base_delay
        self.current_delay = base_delay
        self.success_count = 0
        self.failure_count = 0
        self.min_delay = 0.5
        self.max_delay = 10.0
    
    def adjust_delay(self, success: bool, response_time: Optional[float] = None) -> float:
        """Adjust delay based on success/failure"""
        if success:
            self.success_count += 1
            self.failure_count = 0
            
            # Speed up after consecutive successes
            if self.success_count > 5:
                self.current_delay = max(self.min_delay, self.current_delay * 0.9)
        else:
            self.failure_count += 1
            self.success_count = 0
            
            # Slow down after failures
            self.current_delay = min(self.max_delay, self.current_delay * 1.5)
        
        # Add jitter to avoid detection
        jitter = random.uniform(0.8, 1.2)
        return self.current_delay * jitter

class DataValidator:
    """Data quality validation and scoring"""
    
    def __init__(self):
        self.suspicious_keywords = [
            'captcha', 'robot', 'blocked', 'access denied', 'forbidden',
            'rate limit', 'too many requests', 'bot detection'
        ]
    
    def validate_scraped_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate scraped data and return quality score"""
        quality_score = 0
        issues = []
        
        # Check for essential content
        if data.get('title') and len(data['title'].strip()) > 5:
            quality_score += 20
        else:
            issues.append("Missing or short title")
        
        # Check content richness
        paragraphs = data.get('paragraphs', [])
        paragraph_count = len(paragraphs)
        total_content_length = sum(len(p) for p in paragraphs)
        
        if paragraph_count > 3 and total_content_length > 500:
            quality_score += 30
        elif paragraph_count > 0 and total_content_length > 100:
            quality_score += 15
        else:
            issues.append("No meaningful content found")
        
        # Check for links
        if data.get('links') and len(data['links']) > 0:
            quality_score += 10
        
        # Check for suspicious patterns (bot detection pages)
        content_text = ' '.join(paragraphs).lower()
        if any(keyword in content_text for keyword in self.suspicious_keywords):
            quality_score -= 50
            issues.append("Possible bot detection page")
        
        return {
            'quality_score': max(0, quality_score),
            'is_valid': quality_score > 40,
            'issues': issues,
            'content_length': total_content_length,
            'paragraph_count': paragraph_count
        }

class PerformanceMonitor:
    """Performance monitoring and metrics collection"""
    
    def __init__(self):
        self.metrics = {
            'requests_per_minute': 0,
            'average_response_time': 0,
            'success_rate': 0,
            'average_quality_score': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }
        self.response_times = []
        self.quality_scores = []
        self.alerts = []
    
    def record_request(self, url: str, success: bool, response_time: float, 
                      quality_score: Optional[int] = None):
        """Record request metrics"""
        self.metrics['total_requests'] += 1
        
        if success:
            self.metrics['successful_requests'] += 1
        else:
            self.metrics['failed_requests'] += 1
        
        # Update response times
        self.response_times.append(response_time)
        if len(self.response_times) > 100:  # Keep last 100
            self.response_times.pop(0)
        
        # Update quality scores
        if quality_score is not None:
            self.quality_scores.append(quality_score)
            if len(self.quality_scores) > 100:
                self.quality_scores.pop(0)
        
        # Update calculated metrics
        self._update_metrics()
        
        # Check for alerts
        self._check_performance_alerts()
    
    def _update_metrics(self):
        """Update calculated metrics"""
        if self.metrics['total_requests'] > 0:
            self.metrics['success_rate'] = (
                self.metrics['successful_requests'] / self.metrics['total_requests']
            )
        
        if self.response_times:
            self.metrics['average_response_time'] = sum(self.response_times) / len(self.response_times)
        
        if self.quality_scores:
            self.metrics['average_quality_score'] = sum(self.quality_scores) / len(self.quality_scores)
    
    def _check_performance_alerts(self):
        """Check for performance issues"""
        self.alerts = []  # Clear old alerts
        
        if self.metrics['success_rate'] < 0.8 and self.metrics['total_requests'] > 10:
            self.alerts.append("Low success rate detected")
        
        if self.metrics['average_response_time'] > 10:
            self.alerts.append("High response times detected")
        
        if self.metrics['average_quality_score'] < 50 and len(self.quality_scores) > 5:
            self.alerts.append("Low data quality detected")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        return self.metrics.copy()
    
    def get_alerts(self) -> List[str]:
        """Get current alerts"""
        return self.alerts.copy()

class AdvancedWebScraper:
    def __init__(self, use_proxies=False, proxy_list=None, ignore_robots=True, 
                 use_selenium=False, max_retries=3):
        self.session = requests.Session()
        self.use_proxies = use_proxies
        self.ignore_robots = ignore_robots
        self.use_selenium = use_selenium and HAS_SELENIUM
        self.driver = None
        
        # Set up user agent
        if HAS_FAKE_USERAGENT:
            self.ua = UserAgent()
        else:
            # Fallback user agents
            self.fallback_user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]
        
        # Enhanced components
        self.retry_manager = RetryManager(max_retries=max_retries)
        self.proxy_manager = ProxyManager(proxy_list or []) if use_proxies else None
        self.rate_limiter = AdaptiveRateLimiter()
        self.data_validator = DataValidator()
        self.performance_monitor = PerformanceMonitor()
        
        if self.use_selenium:
            self._setup_selenium()
    
    def _setup_selenium(self):
        """Setup headless Chrome browser for JavaScript rendering"""
        if not HAS_SELENIUM:
            logger.warning("Selenium not available, disabling JavaScript rendering")
            self.use_selenium = False
            return
            
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"--user-agent={self._get_user_agent()}")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.use_selenium = False

    def _get_user_agent(self):
        """Get a random user agent"""
        if HAS_FAKE_USERAGENT:
            try:
                return self.ua.random
            except:
                pass
        
        # Fallback to predefined user agents
        return random.choice(self.fallback_user_agents)

    def _get_headers(self):
        """Generate realistic browser headers"""
        return {
            'User-Agent': self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def _get_proxy(self):
        """Get the best available proxy"""
        if self.proxy_manager:
            return self.proxy_manager.get_best_proxy()
        return None

    def _check_robots_txt(self, url):
        """Check if URL is allowed by robots.txt (if not ignoring)"""
        if self.ignore_robots or not HAS_ROBOTPARSER:
            return True
        
        try:
            parsed_url = urllib.parse.urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
            
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            user_agent = self._get_user_agent()
            allowed = rp.can_fetch(user_agent, url)
            
            if not allowed:
                logger.warning(f"URL {url} is disallowed by robots.txt")
            
            return allowed
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True  # Allow if we can't check

    def fetch_page_requests(self, url):
        """Fetch page using requests with enhanced error handling"""
        def _fetch():
            headers = self._get_headers()
            proxy = self._get_proxy()
            proxies = {'http': proxy, 'https': proxy} if proxy else None
            
            start_time = time.time()
            response = self.session.get(url, headers=headers, proxies=proxies, timeout=30)
            response_time = time.time() - start_time
            
            # Update proxy performance
            if self.proxy_manager and proxy:
                success = response.status_code == 200
                self.proxy_manager.update_proxy_performance(proxy, success, response_time)
            
            response.raise_for_status()
            return response.text, response_time
        
        return self.retry_manager.retry_with_backoff(_fetch)

    def fetch_page_selenium(self, url):
        """Fetch page using Selenium with enhanced error handling"""
        def _fetch():
            if not self.driver:
                raise Exception("Selenium driver not initialized")
            
            start_time = time.time()
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            response_time = time.time() - start_time
            return self.driver.page_source, response_time
        
        return self.retry_manager.retry_with_backoff(_fetch)

    def fetch_page(self, url):
        """Fetch page content with appropriate method"""
        if self.use_selenium:
            return self.fetch_page_selenium(url)
        else:
            return self.fetch_page_requests(url)

    def parse_html(self, html_content):
        """Parse HTML content"""
        if html_content:
            return BeautifulSoup(html_content, 'html.parser')  # Use built-in parser as fallback
        return None

    def extract_data(self, soup, url):
        """Extract comprehensive data from parsed HTML"""
        if not soup:
            return None
        
        data = {
            'url': url,
            'title': '',
            'meta_description': '',
            'headings': [],
            'paragraphs': [],
            'links': [],
            'images': [],
            'structured_data': [],
            'content_hash': ''
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            data['title'] = title_tag.get_text().strip()
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data['meta_description'] = meta_desc.get('content', '').strip()
        
        # Extract headings
        for i in range(1, 7):
            for heading in soup.find_all(f'h{i}'):
                data['headings'].append({
                    'level': i,
                    'text': heading.get_text().strip()
                })
        
        # Extract paragraphs
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 10:  # Filter out short paragraphs
                data['paragraphs'].append(text)
        
        # Extract links
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            text = link.get_text().strip()
            if href and text:
                data['links'].append({
                    'url': href,
                    'text': text
                })
        
        # Extract images
        for img in soup.find_all('img'):
            src = img.get('src', '').strip()
            alt = img.get('alt', '').strip()
            if src:
                data['images'].append({
                    'src': src,
                    'alt': alt
                })
        
        # Extract structured data (JSON-LD)
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                if script.string:
                    structured_data = json.loads(script.string)
                    data['structured_data'].append(structured_data)
            except:
                continue
        
        # Generate content hash for deduplication
        content_text = ' '.join(data['paragraphs'])
        data['content_hash'] = hashlib.md5(content_text.encode()).hexdigest()
        
        return data

    def scrape(self, url):
        """Scrape a single URL with enhanced error handling and monitoring"""
        logger.info(f"Scraping: {url}")
        
        if not self._check_robots_txt(url):
            logger.warning(f"Skipping {url} due to robots.txt restrictions")
            return None
        
        try:
            # Fetch page
            html_content, response_time = self.fetch_page(url)
            
            # Parse HTML
            soup = self.parse_html(html_content)
            if not soup:
                logger.error(f"Failed to parse HTML for {url}")
                self.performance_monitor.record_request(url, False, response_time)
                return None
            
            # Extract data
            data = self.extract_data(soup, url)
            if not data:
                logger.error(f"Failed to extract data from {url}")
                self.performance_monitor.record_request(url, False, response_time)
                return None
            
            # Validate data quality
            validation_result = self.data_validator.validate_scraped_data(data)
            data['validation'] = validation_result
            
            # Record successful request
            self.performance_monitor.record_request(
                url, True, response_time, validation_result['quality_score']
            )
            
            logger.info(f"Successfully scraped {url} (Quality: {validation_result['quality_score']})")
            return data
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            self.performance_monitor.record_request(url, False, 0)
            return None

    def scrape_multiple(self, urls):
        """Scrape multiple URLs with progress tracking"""
        results = []
        total_urls = len(urls)
        
        logger.info(f"Starting to scrape {total_urls} URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Progress: {i}/{total_urls} - {url}")
            
            data = self.scrape(url)
            if data:
                results.append(data)
            
            # Add delay between requests
            if i < total_urls:
                delay = self.rate_limiter.adjust_delay(True)
                time.sleep(delay)
        
        logger.info(f"Completed scraping. Success: {len(results)}/{total_urls}")
        return results

    def save_data(self, data, filename):
        """Save scraped data to file with metadata"""
        output_data = {
            'metadata': {
                'scraped_at': datetime.now().isoformat(),
                'total_items': len(data),
                'performance_metrics': self.performance_monitor.get_metrics(),
                'alerts': self.performance_monitor.get_alerts()
            },
            'data': data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data saved to {filename}")

    def get_performance_metrics(self):
        """Get current performance metrics"""
        return self.performance_monitor.get_metrics()

    def get_alerts(self):
        """Get current performance alerts"""
        return self.performance_monitor.get_alerts()

    def close(self):
        """Clean up resources"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Selenium WebDriver closed")
            except:
                pass
        
        if self.session:
            try:
                self.session.close()
                logger.info("Requests session closed")
            except:
                pass

def main():
    """Example usage of the enhanced scraper"""
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=False
    )
    
    try:
        # Scrape a test URL
        data = scraper.scrape("https://httpbin.org/html")
        
        if data:
            print(f"Successfully scraped data:")
            print(f"Title: {data['title']}")
            print(f"Quality Score: {data['validation']['quality_score']}")
            print(f"Paragraphs: {len(data['paragraphs'])}")
            
            # Save results
            scraper.save_data([data], "enhanced_scraping_results.json")
        
        # Print performance metrics
        metrics = scraper.get_performance_metrics()
        print(f"\nPerformance Metrics:")
        print(f"Success Rate: {metrics['success_rate']:.2%}")
        print(f"Average Response Time: {metrics['average_response_time']:.2f}s")
        print(f"Average Quality Score: {metrics['average_quality_score']:.1f}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
