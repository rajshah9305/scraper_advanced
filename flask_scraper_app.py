import os
import json
import time
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading
from advanced_scraper import AdvancedWebScraper
import logging
from werkzeug.utils import secure_filename
import zipfile
import tempfile
import hashlib
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'

# Initialize SocketIO for real-time updates with threading async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store active scraping jobs with enhanced tracking
active_jobs = {}

@dataclass
class ScrapingJob:
    job_id: str
    urls: List[str]
    config: Dict[str, Any]
    status: str = 'starting'
    progress: int = 0
    results: List[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = None
    alerts: List[str] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []
        if self.errors is None:
            self.errors = []
        if self.start_time is None:
            self.start_time = datetime.now()
        if self.performance_metrics is None:
            self.performance_metrics = {}
        if self.alerts is None:
            self.alerts = []
    
    def to_dict(self):
        return {
            'job_id': self.job_id,
            'status': self.status,
            'progress': self.progress,
            'total_urls': len(self.urls),
            'completed_urls': len(self.results),
            'errors': len(self.errors),
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'results_count': len(self.results),
            'performance_metrics': self.performance_metrics,
            'alerts': self.alerts,
            'success_rate': (len(self.results) / len(self.urls) * 100) if self.urls else 0
        }

class EnhancedScrapingManager:
    """Enhanced scraping manager with performance monitoring"""
    
    def __init__(self):
        self.jobs = {}
        self.global_metrics = {
            'total_jobs': 0,
            'active_jobs': 0,
            'total_urls_scraped': 0,
            'average_success_rate': 0,
            'average_quality_score': 0
        }
    
    def create_job(self, job_id: str, urls: List[str], config: Dict[str, Any]) -> ScrapingJob:
        """Create a new scraping job"""
        job = ScrapingJob(job_id=job_id, urls=urls, config=config)
        self.jobs[job_id] = job
        self.global_metrics['total_jobs'] += 1
        self.global_metrics['active_jobs'] += 1
        return job
    
    def update_job_metrics(self, job_id: str, scraper: AdvancedWebScraper):
        """Update job with scraper performance metrics"""
        if job_id in self.jobs:
            job = self.jobs[job_id]
            job.performance_metrics = scraper.get_performance_metrics()
            job.alerts = scraper.get_alerts()
    
    def get_job(self, job_id: str) -> Optional[ScrapingJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def get_global_metrics(self) -> Dict[str, Any]:
        """Get global performance metrics"""
        return self.global_metrics.copy()

# Initialize enhanced scraping manager
scraping_manager = EnhancedScrapingManager()

@app.route('/')
def index():
    """Main scraper interface"""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def start_scraping():
    """Start a new scraping job with enhanced configuration"""
    try:
        data = request.json
        
        # Extract URLs
        urls = []
        if data.get('urls'):
            # Multiple URLs from textarea
            urls = [url.strip() for url in data['urls'].split('\n') if url.strip()]
        elif data.get('single_url'):
            # Single URL
            urls = [data['single_url'].strip()]
        
        if not urls:
            return jsonify({'error': 'No URLs provided'}), 400
        
        # Enhanced configuration
        config = {
            'use_proxies': data.get('use_proxies', False),
            'proxy_list': [p.strip() for p in data.get('proxy_list', '').split('\n') if p.strip()],
            'ignore_robots': data.get('ignore_robots', True),
            'use_selenium': data.get('use_selenium', False),
            'delay_min': float(data.get('delay_min', 1)),
            'delay_max': float(data.get('delay_max', 3)),
            'max_retries': int(data.get('max_retries', 3)),
            'timeout': int(data.get('timeout', 30))
        }
        
        # Create job
        job_id = str(uuid.uuid4())
        job = scraping_manager.create_job(job_id, urls, config)
        
        # Start scraping in background thread
        thread = threading.Thread(target=run_enhanced_scraping_job, args=(job,))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'total_urls': len(urls),
            'message': f'Started scraping {len(urls)} URLs'
        })
        
    except Exception as e:
        logger.error(f"Error starting scraping job: {e}")
        return jsonify({'error': str(e)}), 500

def run_enhanced_scraping_job(job: ScrapingJob):
    """Run enhanced scraping job with performance monitoring"""
    try:
        job.status = 'running'
        emit_job_update(job, "Starting scraping job...")
        
        # Initialize scraper with enhanced configuration
        scraper = AdvancedWebScraper(
            use_proxies=job.config.get('use_proxies', False),
            proxy_list=job.config.get('proxy_list', []),
            ignore_robots=job.config.get('ignore_robots', True),
            use_selenium=job.config.get('use_selenium', False),
            max_retries=job.config.get('max_retries', 3)
        )
        
        total_urls = len(job.urls)
        
        for i, url in enumerate(job.urls, 1):
            try:
                # Update progress
                job.progress = int((i - 1) / total_urls * 100)
                emit_job_update(job, f"Scraping {i}/{total_urls}: {url}")
                
                # Scrape URL
                data = scraper.scrape(url)
                
                if data:
                    job.results.append(data)
                    emit_job_update(job, f"Successfully scraped: {url}")
                else:
                    error_info = {
                        'url': url,
                        'error': 'Failed to scrape data',
                        'timestamp': datetime.now().isoformat()
                    }
                    job.errors.append(error_info)
                    emit_job_update(job, f"Failed to scrape: {url}")
                
                # Update job metrics
                scraping_manager.update_job_metrics(job.job_id, scraper)
                
                # Add delay between requests
                if i < total_urls:
                    delay = scraper.rate_limiter.adjust_delay(True)
                    time.sleep(delay)
                
            except Exception as e:
                error_info = {
                    'url': url,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                job.errors.append(error_info)
                emit_job_update(job, f"Error scraping {url}: {str(e)}")
        
        # Finalize job
        job.status = 'completed'
        job.progress = 100
        job.end_time = datetime.now()
        
        # Update global metrics
        scraping_manager.global_metrics['active_jobs'] -= 1
        scraping_manager.global_metrics['total_urls_scraped'] += len(job.results)
        
        # Save results
        if job.results:
            filename = f"scraping_results_{job.job_id}.json"
            filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
            scraper.save_data(job.results, filepath)
            job.results_file = filepath
        
        emit_job_update(job, "Scraping job completed!")
        scraper.close()
        
    except Exception as e:
        job.status = 'failed'
        job.end_time = datetime.now()
        emit_job_update(job, f"Job failed: {str(e)}")
        logger.error(f"Scraping job failed: {e}")

def emit_job_update(job: ScrapingJob, message: str = None):
    """Emit job update via WebSocket"""
    try:
        job_data = job.to_dict()
        if message:
            job_data['message'] = message
        
        socketio.emit('job_update', job_data, room=job.job_id)
    except Exception as e:
        logger.error(f"Error emitting job update: {e}")

@app.route('/api/job/<job_id>')
def get_job_status(job_id):
    """Get job status with enhanced metrics"""
    job = scraping_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job.to_dict())

@app.route('/api/job/<job_id>/results')
def get_job_results(job_id):
    """Get job results with quality analysis"""
    job = scraping_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    # Enhanced results with quality analysis
    enhanced_results = []
    for result in job.results:
        enhanced_result = result.copy()
        if 'validation' in result:
            enhanced_result['quality_score'] = result['validation']['quality_score']
            enhanced_result['is_valid'] = result['validation']['is_valid']
            enhanced_result['issues'] = result['validation']['issues']
        
        enhanced_results.append(enhanced_result)
    
    return jsonify({
        'job_id': job_id,
        'results': enhanced_results,
        'total_results': len(enhanced_results),
        'success_rate': len(enhanced_results) / len(job.urls) * 100 if job.urls else 0
    })

@app.route('/api/job/<job_id>/download')
def download_results(job_id):
    """Download results as JSON with enhanced metadata"""
    job = scraping_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if not job.results:
        return jsonify({'error': 'No results available'}), 404
    
    # Create enhanced output with metadata
    output_data = {
        'metadata': {
            'job_id': job_id,
            'scraped_at': datetime.now().isoformat(),
            'total_urls': len(job.urls),
            'successful_scrapes': len(job.results),
            'failed_scrapes': len(job.errors),
            'success_rate': len(job.results) / len(job.urls) * 100 if job.urls else 0,
            'performance_metrics': job.performance_metrics,
            'alerts': job.alerts,
            'job_duration': (job.end_time - job.start_time).total_seconds() if job.end_time else 0
        },
        'results': job.results,
        'errors': job.errors
    }
    
    # Create file in memory
    output = io.StringIO()
    json.dump(output_data, output, indent=2, ensure_ascii=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'scraping_results_{job_id}.json'
    )

@app.route('/api/job/<job_id>/download-csv')
def download_results_csv(job_id):
    """Download results as CSV with enhanced formatting"""
    job = scraping_manager.get_job(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    if not job.results:
        return jsonify({'error': 'No results available'}), 404
    
    # Create CSV output
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'URL', 'Title', 'Meta Description', 'Paragraphs Count', 
        'Links Count', 'Images Count', 'Quality Score', 'Is Valid', 'Issues'
    ])
    
    # Write data rows
    for result in job.results:
        quality_score = result.get('validation', {}).get('quality_score', 0)
        is_valid = result.get('validation', {}).get('is_valid', False)
        issues = '; '.join(result.get('validation', {}).get('issues', []))
        
        writer.writerow([
            result.get('url', ''),
            result.get('title', ''),
            result.get('meta_description', ''),
            len(result.get('paragraphs', [])),
            len(result.get('links', [])),
            len(result.get('images', [])),
            quality_score,
            is_valid,
            issues
        ])
    
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'scraping_results_{job_id}.csv'
    )

@app.route('/api/upload-urls', methods=['POST'])
def upload_urls():
    """Upload URLs from file with enhanced validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Read URLs from file
            urls = []
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    url = line.strip()
                    if url and url.startswith(('http://', 'https://')):
                        urls.append(url)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'urls': urls,
                'count': len(urls),
                'message': f'Successfully loaded {len(urls)} URLs'
            })
    
    except Exception as e:
        logger.error(f"Error uploading URLs: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics')
def get_analytics():
    """Get global analytics and performance metrics"""
    global_metrics = scraping_manager.get_global_metrics()
    
    # Calculate additional metrics
    active_jobs = [job for job in scraping_manager.jobs.values() if job.status == 'running']
    completed_jobs = [job for job in scraping_manager.jobs.values() if job.status == 'completed']
    
    analytics = {
        'global_metrics': global_metrics,
        'active_jobs_count': len(active_jobs),
        'completed_jobs_count': len(completed_jobs),
        'recent_jobs': [
            {
                'job_id': job.job_id,
                'status': job.status,
                'total_urls': len(job.urls),
                'success_rate': len(job.results) / len(job.urls) * 100 if job.urls else 0,
                'start_time': job.start_time.isoformat()
            }
            for job in list(scraping_manager.jobs.values())[-10:]  # Last 10 jobs
        ]
    }
    
    return jsonify(analytics)

@socketio.on('join_job')
def on_join_job(data):
    """Join job room for real-time updates"""
    job_id = data.get('job_id')
    if job_id:
        join_room(job_id)
        emit('status', {'message': f'Joined job room: {job_id}'})

@socketio.on('leave_job')
def on_leave_job(data):
    """Leave job room"""
    job_id = data.get('job_id')
    if job_id:
        leave_room(job_id)
        emit('status', {'message': f'Left job room: {job_id}'})

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'active_jobs': scraping_manager.global_metrics['active_jobs']
    })

if __name__ == '__main__':
    logger.info("Starting Elite Web Scraper Flask application...")
    port = int(os.environ.get('PORT', 5000))
    # Use simple Flask development server for deployment compatibility
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
