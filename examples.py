#!/usr/bin/env python3
"""
Elite Web Scraper - Enhanced Usage Examples

This file contains practical examples of how to use the enhanced AdvancedWebScraper
for different scenarios and use cases, including the new performance monitoring,
data validation, and advanced error handling features.
"""

from advanced_scraper import AdvancedWebScraper
import json
import time
from typing import List, Dict, Any

def example_enhanced_basic_scraping():
    """Example 1: Enhanced basic web scraping with performance monitoring"""
    print("=== Example 1: Enhanced Basic Web Scraping ===")
    
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=False,
        max_retries=3
    )
    
    try:
        # Scrape a simple website
        url = "https://quotes.toscrape.com/"
        print(f"Scraping: {url}")
        
        data = scraper.scrape(url)
        
        if data:
            print(f"✓ Successfully scraped {url}")
            print(f"  Title: {data['title']}")
            print(f"  Quality Score: {data['validation']['quality_score']}")
            print(f"  Is Valid: {data['validation']['is_valid']}")
            print(f"  Issues: {data['validation']['issues']}")
            print(f"  Paragraphs found: {len(data['paragraphs'])}")
            print(f"  Links found: {len(data['links'])}")
            print(f"  Images found: {len(data['images'])}")
            
            # Get performance metrics
            metrics = scraper.get_performance_metrics()
            print(f"  Performance Metrics:")
            print(f"    Success Rate: {metrics['success_rate']:.2%}")
            print(f"    Average Response Time: {metrics['average_response_time']:.2f}s")
            print(f"    Average Quality Score: {metrics['average_quality_score']:.1f}")
            
            # Check for alerts
            alerts = scraper.get_alerts()
            if alerts:
                print(f"  Alerts: {alerts}")
            
            # Save to file
            scraper.save_data([data], "example1_enhanced_output.json")
            print("  Data saved to example1_enhanced_output.json")
        else:
            print("✗ Failed to scrape data")
            
    finally:
        scraper.close()
    
    print()

def example_enhanced_javascript_scraping():
    """Example 2: Enhanced JavaScript-heavy website scraping with Selenium"""
    print("=== Example 2: Enhanced JavaScript-Heavy Website Scraping ===")
    
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=True,  # Enable Selenium for JS rendering
        max_retries=3
    )
    
    try:
        # Scrape a website that requires JavaScript
        url = "https://httpbin.org/html"
        print(f"Scraping with Selenium: {url}")
        
        data = scraper.scrape(url)
        
        if data:
            print(f"✓ Successfully scraped {url} with Selenium")
            print(f"  Title: {data['title']}")
            print(f"  Quality Score: {data['validation']['quality_score']}")
            print(f"  Content extracted: {len(data['paragraphs'])} paragraphs")
            print(f"  Structured data found: {len(data['structured_data'])} items")
            
            # Save to file
            scraper.save_data([data], "example2_enhanced_output.json")
            print("  Data saved to example2_enhanced_output.json")
        else:
            print("✗ Failed to scrape data")
            
    finally:
        scraper.close()
    
    print()

def example_enhanced_multiple_urls():
    """Example 3: Enhanced multiple URL scraping with progress tracking"""
    print("=== Example 3: Enhanced Multiple URL Scraping ===")
    
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=False,
        max_retries=3
    )
    
    try:
        # List of URLs to scrape
        urls = [
            "https://httpbin.org/html",
            "https://quotes.toscrape.com/",
            "https://httpbin.org/json",
            "https://httpbin.org/xml"
        ]
        
        print(f"Scraping {len(urls)} URLs with enhanced monitoring...")
        
        results = scraper.scrape_multiple(urls)
        
        if results:
            print(f"✓ Successfully scraped {len(results)} URLs")
            
            # Analyze results
            total_quality_score = 0
            valid_results = 0
            total_content_length = 0
            
            for i, result in enumerate(results, 1):
                quality_score = result['validation']['quality_score']
                is_valid = result['validation']['is_valid']
                content_length = result['validation']['content_length']
                
                total_quality_score += quality_score
                total_content_length += content_length
                if is_valid:
                    valid_results += 1
                
                print(f"  {i}. {result['url']}")
                print(f"     Quality: {quality_score}/100, Valid: {is_valid}")
                print(f"     Content: {content_length} chars, {len(result['paragraphs'])} paragraphs")
            
            # Summary statistics
            avg_quality = total_quality_score / len(results)
            success_rate = valid_results / len(results) * 100
            avg_content_length = total_content_length / len(results)
            
            print(f"\nSummary:")
            print(f"  Average Quality Score: {avg_quality:.1f}/100")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Average Content Length: {avg_content_length:.0f} characters")
            
            # Get performance metrics
            metrics = scraper.get_performance_metrics()
            print(f"  Performance Metrics:")
            print(f"    Success Rate: {metrics['success_rate']:.2%}")
            print(f"    Average Response Time: {metrics['average_response_time']:.2f}s")
            
            # Save results
            scraper.save_data(results, "example3_enhanced_output.json")
            print("  Data saved to example3_enhanced_output.json")
        else:
            print("✗ No data scraped")
            
    finally:
        scraper.close()
    
    print()

def example_enhanced_proxy_usage():
    """Example 4: Enhanced proxy usage with health monitoring"""
    print("=== Example 4: Enhanced Proxy Usage ===")
    
    # Example proxy list (replace with real proxies)
    proxy_list = [
        # "http://proxy1.example.com:8080",
        # "http://proxy2.example.com:8080",
        # "http://proxy3.example.com:8080"
    ]
    
    if not proxy_list:
        print("⚠️  No proxies configured. Using direct connection.")
        proxy_list = []
    
    scraper = AdvancedWebScraper(
        use_proxies=bool(proxy_list),
        proxy_list=proxy_list,
        ignore_robots=True,
        use_selenium=False,
        max_retries=3
    )
    
    try:
        urls = [
            "https://httpbin.org/ip",
            "https://httpbin.org/user-agent",
            "https://httpbin.org/headers"
        ]
        
        print(f"Scraping {len(urls)} URLs with proxy rotation...")
        
        for i, url in enumerate(urls, 1):
            print(f"Scraping {i}/{len(urls)}: {url}")
            
            data = scraper.scrape(url)
            
            if data:
                print(f"  ✓ Success - Quality: {data['validation']['quality_score']}")
                
                # Show proxy information if available
                if scraper.proxy_manager:
                    proxy_metrics = []
                    for proxy in scraper.proxy_manager.proxies:
                        proxy_metrics.append({
                            'url': proxy.url,
                            'health': proxy.health,
                            'response_time': proxy.response_time,
                            'success_count': proxy.success_count,
                            'failure_count': proxy.failure_count
                        })
                    print(f"  Proxy Metrics: {proxy_metrics}")
            else:
                print(f"  ✗ Failed")
            
            # Add delay between requests
            if i < len(urls):
                time.sleep(2)
        
        # Save results
        results = [data for data in [scraper.scrape(url) for url in urls] if data]
        if results:
            scraper.save_data(results, "example4_proxy_output.json")
            print("  Data saved to example4_proxy_output.json")
            
    finally:
        scraper.close()
    
    print()

def example_enhanced_ethical_scraping():
    """Example 5: Enhanced ethical scraping with robots.txt compliance"""
    print("=== Example 5: Enhanced Ethical Scraping ===")
    
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=False,  # Respect robots.txt
        use_selenium=False,
        max_retries=2  # Fewer retries for ethical scraping
    )
    
    try:
        # Test URLs that typically have robots.txt
        urls = [
            "https://www.google.com/robots.txt",  # Should be allowed
            "https://httpbin.org/robots.txt",     # Should be allowed
            "https://quotes.toscrape.com/"        # Should be allowed
        ]
        
        print("Testing ethical scraping with robots.txt compliance...")
        
        for url in urls:
            print(f"Checking: {url}")
            
            # Check robots.txt compliance
            allowed = scraper._check_robots_txt(url)
            print(f"  Robots.txt allows: {allowed}")
            
            if allowed:
                data = scraper.scrape(url)
                if data:
                    print(f"  ✓ Successfully scraped (Quality: {data['validation']['quality_score']})")
                else:
                    print(f"  ✗ Failed to scrape")
            else:
                print(f"  ⚠️  Skipped due to robots.txt restrictions")
        
        # Get performance metrics
        metrics = scraper.get_performance_metrics()
        print(f"\nEthical Scraping Metrics:")
        print(f"  Success Rate: {metrics['success_rate']:.2%}")
        print(f"  Average Response Time: {metrics['average_response_time']:.2f}s")
        
    finally:
        scraper.close()
    
    print()

def example_enhanced_custom_extraction():
    """Example 6: Enhanced custom data extraction with validation"""
    print("=== Example 6: Enhanced Custom Data Extraction ===")
    
    class CustomEnhancedScraper(AdvancedWebScraper):
        def extract_data(self, soup, url):
            # Get the base data
            data = super().extract_data(soup, url)
            
            if not data:
                return None
            
            # Add custom extraction logic
            data['custom_fields'] = {}
            
            # Extract social media links
            social_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                if any(social in href for social in ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com']):
                    social_links.append({
                        'platform': self._identify_social_platform(href),
                        'url': link.get('href'),
                        'text': link.get_text().strip()
                    })
            data['custom_fields']['social_links'] = social_links
            
            # Extract contact information
            contact_info = self._extract_contact_info(soup)
            data['custom_fields']['contact_info'] = contact_info
            
            # Extract meta tags for SEO analysis
            seo_meta = self._extract_seo_meta(soup)
            data['custom_fields']['seo_meta'] = seo_meta
            
            return data
        
        def _identify_social_platform(self, url):
            """Identify social media platform from URL"""
            if 'facebook.com' in url:
                return 'Facebook'
            elif 'twitter.com' in url:
                return 'Twitter'
            elif 'linkedin.com' in url:
                return 'LinkedIn'
            elif 'instagram.com' in url:
                return 'Instagram'
            else:
                return 'Other'
        
        def _extract_contact_info(self, soup):
            """Extract contact information from page"""
            contact_info = {
                'emails': [],
                'phones': [],
                'addresses': []
            }
            
            # Extract emails
            import re
            text = soup.get_text()
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, text)
            contact_info['emails'] = list(set(emails))  # Remove duplicates
            
            # Extract phone numbers
            phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            phones = re.findall(phone_pattern, text)
            contact_info['phones'] = list(set(phones))
            
            return contact_info
        
        def _extract_seo_meta(self, soup):
            """Extract SEO-related meta tags"""
            seo_meta = {}
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                seo_meta['description'] = meta_desc.get('content', '')
            
            # Meta keywords
            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords:
                seo_meta['keywords'] = meta_keywords.get('content', '')
            
            # Open Graph tags
            og_tags = {}
            for tag in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
                property_name = tag.get('property', '').replace('og:', '')
                og_tags[property_name] = tag.get('content', '')
            seo_meta['open_graph'] = og_tags
            
            return seo_meta
    
    scraper = CustomEnhancedScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=False,
        max_retries=3
    )
    
    try:
        url = "https://quotes.toscrape.com/"
        print(f"Scraping with custom extraction: {url}")
        
        data = scraper.scrape(url)
        
        if data:
            print(f"✓ Successfully scraped with custom extraction")
            print(f"  Title: {data['title']}")
            print(f"  Quality Score: {data['validation']['quality_score']}")
            
            # Show custom extracted data
            custom_fields = data.get('custom_fields', {})
            
            if custom_fields.get('social_links'):
                print(f"  Social Links: {len(custom_fields['social_links'])} found")
                for social in custom_fields['social_links'][:3]:  # Show first 3
                    print(f"    - {social['platform']}: {social['url']}")
            
            if custom_fields.get('contact_info'):
                contact = custom_fields['contact_info']
                print(f"  Contact Info:")
                print(f"    Emails: {len(contact['emails'])} found")
                print(f"    Phones: {len(contact['phones'])} found")
            
            if custom_fields.get('seo_meta'):
                seo = custom_fields['seo_meta']
                print(f"  SEO Meta:")
                if seo.get('description'):
                    print(f"    Description: {seo['description'][:100]}...")
                if seo.get('open_graph'):
                    print(f"    Open Graph tags: {len(seo['open_graph'])} found")
            
            # Save enhanced results
            scraper.save_data([data], "example6_custom_extraction.json")
            print("  Enhanced data saved to example6_custom_extraction.json")
        else:
            print("✗ Failed to scrape data")
            
    finally:
        scraper.close()
    
    print()

def example_enhanced_performance_monitoring():
    """Example 7: Enhanced performance monitoring and alerting"""
    print("=== Example 7: Enhanced Performance Monitoring ===")
    
    scraper = AdvancedWebScraper(
        use_proxies=False,
        ignore_robots=True,
        use_selenium=False,
        max_retries=3
    )
    
    try:
        # Test URLs with varying complexity
        urls = [
            "https://httpbin.org/html",           # Simple
            "https://quotes.toscrape.com/",       # Medium
            "https://httpbin.org/delay/2",        # Slow
            "https://httpbin.org/status/404",     # Error
            "https://httpbin.org/status/500"      # Server error
        ]
        
        print("Testing performance monitoring with various scenarios...")
        
        for i, url in enumerate(urls, 1):
            print(f"\nTest {i}/{len(urls)}: {url}")
            
            start_time = time.time()
            data = scraper.scrape(url)
            end_time = time.time()
            
            if data:
                print(f"  ✓ Success")
                print(f"    Response Time: {end_time - start_time:.2f}s")
                print(f"    Quality Score: {data['validation']['quality_score']}")
                print(f"    Content Length: {data['validation']['content_length']}")
            else:
                print(f"  ✗ Failed")
                print(f"    Response Time: {end_time - start_time:.2f}s")
            
            # Show current metrics
            metrics = scraper.get_performance_metrics()
            print(f"    Current Success Rate: {metrics['success_rate']:.2%}")
            print(f"    Average Response Time: {metrics['average_response_time']:.2f}s")
            
            # Check for alerts
            alerts = scraper.get_alerts()
            if alerts:
                print(f"    ⚠️  Alerts: {alerts}")
        
        # Final performance summary
        print(f"\n=== Final Performance Summary ===")
        final_metrics = scraper.get_performance_metrics()
        print(f"Total Requests: {final_metrics['total_requests']}")
        print(f"Success Rate: {final_metrics['success_rate']:.2%}")
        print(f"Average Response Time: {final_metrics['average_response_time']:.2f}s")
        print(f"Average Quality Score: {final_metrics['average_quality_score']:.1f}")
        
        final_alerts = scraper.get_alerts()
        if final_alerts:
            print(f"Active Alerts: {final_alerts}")
        
    finally:
        scraper.close()
    
    print()

def main():
    """Run all enhanced examples"""
    print("🚀 Elite Web Scraper - Enhanced Examples")
    print("=" * 50)
    
    examples = [
        example_enhanced_basic_scraping,
        example_enhanced_javascript_scraping,
        example_enhanced_multiple_urls,
        example_enhanced_proxy_usage,
        example_enhanced_ethical_scraping,
        example_enhanced_custom_extraction,
        example_enhanced_performance_monitoring
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"❌ Error in example: {e}")
            print()
    
    print("✅ All enhanced examples completed!")

if __name__ == "__main__":
    main()

