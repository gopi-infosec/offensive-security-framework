from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application configuration with environment variables"""
    
    # API Configuration
    perplexity_api_key: str
    perplexity_model: str = "sonar-pro"
    perplexity_api_url: str = "https://api.perplexity.ai/chat/completions"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Tool Paths
    subfinder_path: str = "subfinder"
    httpx_path: str = "httpx"
    nmap_path: str = "nmap"  # Added nmap
    naabu_path: str = "naabu"
    gau_path: str = "gau"
    ffuf_path: str = "ffuf"
    
    # Nmap Configuration
    nmap_top_ports: int = 1000  # Scan top 1000 ports
    nmap_timing: str = "T4"  # Aggressive timing (T0-T5)
    nmap_max_hosts: int = 10  # Max hosts to scan (performance)
    
    # Timeouts (seconds)
    scan_timeout: int = 300
    port_scan_timeout: int = 180  # Dedicated timeout for port scanning
    ai_timeout: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

