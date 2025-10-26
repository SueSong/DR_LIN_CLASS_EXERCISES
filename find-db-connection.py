#!/usr/bin/env python3
"""
Database Connection Finder Script
Searches for database connection details in a GraphQL API installation
Cross-platform Python version with advanced pattern matching
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fnmatch

class DatabaseConnectionFinder:
    def __init__(self, target_dir: str):
        self.target_dir = Path(target_dir)
        self.results = []
        
        # Database connection patterns
        self.patterns = {
            'env_vars': [
                r'DATABASE_URL\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'DB_HOST\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'DB_USER\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'DB_PASSWORD\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'DB_NAME\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'DB_PORT\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'MONGODB?_URI\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'POSTGRES_URI\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'MYSQL_URI\s*=\s*["\']?([^"\'\s]+)["\']?',
                r'REDIS_URI\s*=\s*["\']?([^"\'\s]+)["\']?',
            ],
            'connection_urls': [
                r'(mongodb://[^\s"\']+)',
                r'(postgresql://[^\s"\']+)',
                r'(mysql://[^\s"\']+)',
                r'(redis://[^\s"\']+)',
                r'(sqlite://[^\s"\']+)',
            ],
            'json_config': [
                r'"host"\s*:\s*"([^"]+)"',
                r'"user"\s*:\s*"([^"]+)"',
                r'"password"\s*:\s*"([^"]+)"',
                r'"database"\s*:\s*"([^"]+)"',
                r'"port"\s*:\s*(\d+)',
                r'"connectionString"\s*:\s*"([^"]+)"',
            ],
            'code_patterns': [
                r'mongoose\.connect\s*\(\s*["\']([^"\']+)["\']',
                r'createConnection\s*\(\s*["\']([^"\']+)["\']',
                r'new\s+Pool\s*\(\s*{([^}]+)}',
                r'new\s+Client\s*\(\s*["\']([^"\']+)["\']',
            ]
        }
        
        # File extensions to search
        self.file_extensions = [
            '*.env*', '*.config.*', '*.json', '*.js', '*.ts', '*.jsx', '*.tsx',
            '*.py', '*.php', '*.yml', '*.yaml', '*.toml', '*.ini', '*.conf',
            'docker-compose*', 'Dockerfile*', '*.sql', '*.graphql', '*.gql'
        ]
        
        # Sensitive patterns to mask
        self.sensitive_patterns = [
            r'(password\s*[=:]\s*)["\']?[^"\'\s]+["\']?',
            r'(PASSWORD\s*[=:]\s*)["\']?[^"\'\s]+["\']?',
            r'(pass\s*[=:]\s*)["\']?[^"\'\s]+["\']?',
        ]

    def find_files(self) -> List[Path]:
        """Find all relevant files in the target directory"""
        files = []
        
        for pattern in self.file_extensions:
            files.extend(self.target_dir.rglob(pattern))
        
        # Also search for files without extensions that might be config files
        for file_path in self.target_dir.rglob('*'):
            if file_path.is_file() and not file_path.suffix:
                name = file_path.name.lower()
                if any(keyword in name for keyword in ['config', 'env', 'database', 'db']):
                    files.append(file_path)
        
        return list(set(files))  # Remove duplicates

    def mask_sensitive_data(self, content: str) -> str:
        """Mask sensitive information like passwords"""
        masked_content = content
        for pattern in self.sensitive_patterns:
            masked_content = re.sub(pattern, r'\1***MASKED***', masked_content, flags=re.IGNORECASE)
        return masked_content

    def search_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Search for database connection patterns in a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Search for each pattern category
            for category, patterns in self.patterns.items():
                for pattern in patterns:
                    for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
                        line_num = content[:match.start()].count('\n') + 1
                        matched_text = match.group(0)
                        
                        matches.append({
                            'file': str(file_path),
                            'line': line_num,
                            'category': category,
                            'pattern': pattern,
                            'match': self.mask_sensitive_data(matched_text),
                            'context': self.get_context(content, match.start(), match.end())
                        })
                        
        except (PermissionError, UnicodeDecodeError, OSError) as e:
            matches.append({
                'file': str(file_path),
                'error': str(e),
                'category': 'error'
            })
            
        return matches

    def get_context(self, content: str, start: int, end: int, context_lines: int = 2) -> str:
        """Get surrounding context for a match"""
        lines = content.split('\n')
        match_line = content[:start].count('\n')
        
        start_line = max(0, match_line - context_lines)
        end_line = min(len(lines), match_line + context_lines + 1)
        
        context_lines_list = []
        for i in range(start_line, end_line):
            prefix = ">>> " if i == match_line else "    "
            context_lines_list.append(f"{prefix}{i+1:3d}: {lines[i]}")
            
        return '\n'.join(context_lines_list)

    def analyze_package_json(self, file_path: Path) -> Dict[str, Any]:
        """Analyze package.json for database-related dependencies"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            db_deps = {}
            for dep_type in ['dependencies', 'devDependencies']:
                if dep_type in data:
                    for dep, version in data[dep_type].items():
                        if any(keyword in dep.lower() for keyword in 
                               ['mongo', 'postgres', 'mysql', 'redis', 'sqlite', 
                                'prisma', 'typeorm', 'sequelize', 'knex', 'mongoose']):
                            db_deps[dep] = version
                            
            return {
                'file': str(file_path),
                'database_dependencies': db_deps,
                'category': 'package_analysis'
            }
            
        except (json.JSONDecodeError, OSError):
            return {'file': str(file_path), 'error': 'Could not parse JSON', 'category': 'error'}

    def search_all(self) -> Dict[str, Any]:
        """Search all files and return comprehensive results"""
        if not self.target_dir.exists():
            return {'error': f'Target directory does not exist: {self.target_dir}'}
            
        print(f"🔍 Searching for database connections in: {self.target_dir}")
        print("=" * 60)
        
        files = self.find_files()
        print(f"📁 Found {len(files)} files to analyze")
        
        all_matches = []
        package_analyses = []
        
        for file_path in files:
            print(f"🔎 Analyzing: {file_path.name}")
            
            # Special handling for package.json
            if file_path.name == 'package.json':
                package_analyses.append(self.analyze_package_json(file_path))
            
            # Search for patterns
            matches = self.search_file(file_path)
            all_matches.extend(matches)
        
        # Organize results
        results = {
            'target_directory': str(self.target_dir),
            'files_analyzed': len(files),
            'total_matches': len([m for m in all_matches if 'error' not in m]),
            'matches_by_category': {},
            'package_analyses': package_analyses,
            'errors': [m for m in all_matches if 'error' in m],
            'all_matches': all_matches
        }
        
        # Group matches by category
        for match in all_matches:
            if 'category' in match and 'error' not in match:
                category = match['category']
                if category not in results['matches_by_category']:
                    results['matches_by_category'][category] = []
                results['matches_by_category'][category].append(match)
        
        return results

    def print_results(self, results: Dict[str, Any]):
        """Print formatted results"""
        if 'error' in results:
            print(f"❌ {results['error']}")
            return
            
        print(f"\n📊 Analysis Results")
        print("=" * 50)
        print(f"📁 Directory: {results['target_directory']}")
        print(f"📄 Files analyzed: {results['files_analyzed']}")
        print(f"🎯 Total matches: {results['total_matches']}")
        print()
        
        # Print matches by category
        for category, matches in results['matches_by_category'].items():
            print(f"🔍 {category.upper().replace('_', ' ')}")
            print("-" * 40)
            
            for match in matches[:10]:  # Limit to first 10 matches per category
                print(f"📄 {Path(match['file']).name} (line {match['line']})")
                print(f"   Match: {match['match']}")
                if 'context' in match:
                    print("   Context:")
                    print(f"   {match['context']}")
                print()
            
            if len(matches) > 10:
                print(f"   ... and {len(matches) - 10} more matches")
                print()
        
        # Print package analyses
        if results['package_analyses']:
            print("📦 Database Dependencies")
            print("-" * 40)
            for analysis in results['package_analyses']:
                if 'database_dependencies' in analysis and analysis['database_dependencies']:
                    print(f"📄 {Path(analysis['file']).name}")
                    for dep, version in analysis['database_dependencies'].items():
                        print(f"   • {dep}: {version}")
                    print()
        
        # Print errors
        if results['errors']:
            print("⚠️  Errors")
            print("-" * 40)
            for error in results['errors']:
                print(f"📄 {Path(error['file']).name}: {error['error']}")
            print()
        
        print("💡 Common Database Connection Patterns to Look For:")
        print("  • DATABASE_URL=postgresql://user:pass@host:port/dbname")
        print("  • MONGODB_URI=mongodb://user:pass@host:port/dbname")
        print("  • DB_HOST, DB_USER, DB_PASSWORD, DB_NAME, DB_PORT")
        print("  • Connection objects in config files")
        print("  • Docker compose database services")

def main():
    parser = argparse.ArgumentParser(description='Find database connections in a project')
    parser.add_argument('directory', nargs='?', 
                       default='/home/ciuser/www/easiio-chatgpt-devai',
                       help='Target directory to search (default: /home/ciuser/www/easiio-chatgpt-devai)')
    parser.add_argument('--output', '-o', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    finder = DatabaseConnectionFinder(args.directory)
    results = finder.search_all()
    
    finder.print_results(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")

if __name__ == '__main__':
    main()

