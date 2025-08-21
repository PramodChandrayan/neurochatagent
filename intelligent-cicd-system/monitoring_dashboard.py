#!/usr/bin/env python3
"""
📊 Monitoring Dashboard
Live monitoring and control of CI/CD pipelines
"""

import subprocess
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class MonitoringDashboard:
    """Monitors and controls CI/CD pipelines in real-time"""
    
    def __init__(self):
        self.last_status_check = None
        self.status_cache = {}
        self.cache_duration = 30  # seconds
        
    def get_pipeline_status(self) -> Dict[str, any]:
        """Get current pipeline status overview"""
        try:
            # Check if we need to refresh the cache
            if (self.last_status_check and 
                (datetime.now() - self.last_status_check).seconds < self.cache_duration):
                return self.status_cache
            
            # Get recent workflow runs
            runs = self._get_recent_workflow_runs()
            
            # Calculate status metrics
            status = self._calculate_status_metrics(runs)
            
            # Cache the results
            self.status_cache = status
            self.last_status_check = datetime.now()
            
            return status
            
        except Exception as e:
            print(f"❌ Failed to get pipeline status: {str(e)}")
            return {
                'status': 'error',
                'last_run': 'Unknown',
                'success_rate': 0,
                'avg_build_time': 'N/A',
                'error_message': str(e)
            }
    
    def get_recent_runs(self) -> List[Dict[str, any]]:
        """Get recent pipeline runs"""
        try:
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '10', '--json', 
                'number,status,conclusion,startedAt,completedAt,headSha,headBranch,workflowName'
            ], capture_output=True, text=True, check=True)
            
            runs = json.loads(result.stdout)
            
            # Process and format the runs
            formatted_runs = []
            for run in runs:
                formatted_run = {
                    'id': run.get('number'),
                    'status': run.get('status', 'unknown'),
                    'conclusion': run.get('conclusion', 'unknown'),
                    'workflow': run.get('workflowName', 'Unknown'),
                    'branch': run.get('headBranch', 'unknown'),
                    'started_at': run.get('startedAt', ''),
                    'completed_at': run.get('completedAt', ''),
                    'duration': self._calculate_duration(run.get('startedAt'), run.get('completedAt')),
                    'trigger': self._determine_trigger(run)
                }
                formatted_runs.append(formatted_run)
            
            return formatted_runs
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get recent runs: {e.stderr}")
            return []
        except Exception as e:
            print(f"❌ Error getting recent runs: {str(e)}")
            return []
    
    def get_live_logs(self) -> str:
        """Get live logs from the most recent pipeline run"""
        try:
            # Get the most recent run
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '1', '--json', 'number'
            ], capture_output=True, text=True, check=True)
            
            runs = json.loads(result.stdout)
            if not runs:
                return "No pipeline runs found yet."
            
            run_number = runs[0]['number']
            
            # Get logs for this run
            log_result = subprocess.run([
                'gh', 'run', 'view', str(run_number), '--log'
            ], capture_output=True, text=True, check=True)
            
            return log_result.stdout
            
        except subprocess.CalledProcessError as e:
            return f"Failed to get logs: {e.stderr}"
        except Exception as e:
            return f"Error getting logs: {str(e)}"
    
    def trigger_pipeline(self) -> bool:
        """Manually trigger a pipeline run"""
        try:
            print("🚀 Triggering pipeline manually...")
            
            # Trigger the workflow using GitHub CLI
            result = subprocess.run([
                'gh', 'workflow', 'run', 'ci-cd-pipeline.yml'
            ], capture_output=True, text=True, check=True)
            
            if 'Created workflow_run' in result.stdout:
                print("✅ Pipeline triggered successfully!")
                return True
            else:
                print("❌ Failed to trigger pipeline")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to trigger pipeline: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Error triggering pipeline: {str(e)}")
            return False
    
    def get_workflow_status(self, workflow_name: str = 'ci-cd-pipeline.yml') -> Dict[str, any]:
        """Get status of a specific workflow"""
        try:
            result = subprocess.run([
                'gh', 'workflow', 'view', workflow_name, '--json', 
                'name,state,createdAt,updatedAt,path'
            ], capture_output=True, text=True, check=True)
            
            workflow = json.loads(result.stdout)
            
            return {
                'name': workflow.get('name', 'Unknown'),
                'state': workflow.get('state', 'unknown'),
                'created_at': workflow.get('createdAt', ''),
                'updated_at': workflow.get('updatedAt', ''),
                'path': workflow.get('path', '')
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get workflow status: {e.stderr}")
            return {}
        except Exception as e:
            print(f"❌ Error getting workflow status: {str(e)}")
            return {}
    
    def get_run_details(self, run_id: int) -> Dict[str, any]:
        """Get detailed information about a specific run"""
        try:
            result = subprocess.run([
                'gh', 'run', 'view', str(run_id), '--json',
                'number,status,conclusion,startedAt,completedAt,headSha,headBranch,workflowName,url'
            ], capture_output=True, text=True, check=True)
            
            run = json.loads(result.stdout)
            
            return {
                'id': run.get('number'),
                'status': run.get('status', 'unknown'),
                'conclusion': run.get('conclusion', 'unknown'),
                'workflow': run.get('workflowName', 'Unknown'),
                'branch': run.get('headBranch', 'unknown'),
                'started_at': run.get('startedAt', ''),
                'completed_at': run.get('completedAt', ''),
                'duration': self._calculate_duration(run.get('startedAt'), run.get('completedAt')),
                'url': run.get('url', ''),
                'commit_sha': run.get('headSha', '')[:8] if run.get('headSha') else ''
            }
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get run details: {e.stderr}")
            return {}
        except Exception as e:
            print(f"❌ Error getting run details: {str(e)}")
            return {}
    
    def cancel_run(self, run_id: int) -> bool:
        """Cancel a running pipeline"""
        try:
            print(f"🛑 Cancelling run #{run_id}...")
            
            result = subprocess.run([
                'gh', 'run', 'cancel', str(run_id)
            ], capture_output=True, text=True, check=True)
            
            if 'Cancelled' in result.stdout:
                print(f"✅ Run #{run_id} cancelled successfully")
                return True
            else:
                print(f"❌ Failed to cancel run #{run_id}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to cancel run: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Error cancelling run: {str(e)}")
            return False
    
    def rerun_failed_jobs(self, run_id: int) -> bool:
        """Rerun failed jobs from a specific run"""
        try:
            print(f"🔄 Rerunning failed jobs from run #{run_id}...")
            
            result = subprocess.run([
                'gh', 'run', 'rerun', str(run_id), '--failed'
            ], capture_output=True, text=True, check=True)
            
            if 'Created workflow_run' in result.stdout:
                print(f"✅ Failed jobs from run #{run_id} rerun successfully")
                return True
            else:
                print(f"❌ Failed to rerun jobs from run #{run_id}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to rerun failed jobs: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Error rerunning failed jobs: {str(e)}")
            return False
    
    def get_deployment_status(self) -> Dict[str, any]:
        """Get deployment status for Cloud Run services"""
        try:
            # Check if we have GCP access
            result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                                  capture_output=True, text=True, check=True)
            
            project_id = result.stdout.strip()
            
            # Get Cloud Run services
            services_result = subprocess.run([
                'gcloud', 'run', 'services', 'list', '--region', 'us-central1', 
                '--format', 'json'
            ], capture_output=True, text=True, check=True)
            
            services = json.loads(services_result.stdout)
            
            deployment_status = {
                'project_id': project_id,
                'region': 'us-central1',
                'services': []
            }
            
            for service in services:
                service_info = {
                    'name': service.get('metadata', {}).get('name', 'Unknown'),
                    'status': service.get('status', {}).get('conditions', [{}])[0].get('status', 'Unknown'),
                    'url': service.get('status', {}).get('url', 'N/A'),
                    'revision': service.get('status', {}).get('latestReadyRevisionName', 'N/A'),
                    'created_at': service.get('metadata', {}).get('creationTimestamp', 'N/A')
                }
                deployment_status['services'].append(service_info)
            
            return deployment_status
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get deployment status: {e.stderr}")
            return {'error': 'Failed to get deployment status'}
        except Exception as e:
            print(f"❌ Error getting deployment status: {str(e)}")
            return {'error': f'Error: {str(e)}'}
    
    def _get_recent_workflow_runs(self) -> List[Dict[str, any]]:
        """Get recent workflow runs for status calculation"""
        try:
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '20', '--json', 
                'status,conclusion,startedAt,completedAt'
            ], capture_output=True, text=True, check=True)
            
            return json.loads(result.stdout)
            
        except subprocess.CalledProcessError:
            return []
        except Exception:
            return []
    
    def _calculate_status_metrics(self, runs: List[Dict[str, any]]) -> Dict[str, any]:
        """Calculate status metrics from workflow runs"""
        if not runs:
            return {
                'status': 'no_runs',
                'last_run': 'Never',
                'success_rate': 0,
                'avg_build_time': 'N/A'
            }
        
        # Calculate success rate
        successful_runs = sum(1 for run in runs if run.get('conclusion') == 'success')
        total_completed = sum(1 for run in runs if run.get('conclusion') in ['success', 'failure', 'cancelled'])
        success_rate = (successful_runs / total_completed * 100) if total_completed > 0 else 0
        
        # Calculate average build time
        build_times = []
        for run in runs:
            if run.get('startedAt') and run.get('completedAt'):
                duration = self._calculate_duration(run['startedAt'], run['completedAt'])
                if duration != 'N/A':
                    try:
                        # Parse duration like "2m 30s" to minutes
                        parts = duration.split()
                        minutes = 0
                        for part in parts:
                            if 'm' in part:
                                minutes += int(part.replace('m', ''))
                            elif 's' in part:
                                minutes += int(part.replace('s', '')) / 60
                        build_times.append(minutes)
                    except:
                        pass
        
        avg_build_time = f"{sum(build_times) / len(build_times):.1f}m" if build_times else 'N/A'
        
        # Determine overall status
        if total_completed == 0:
            status = 'running'
        elif success_rate >= 80:
            status = 'healthy'
        elif success_rate >= 60:
            status = 'warning'
        else:
            status = 'critical'
        
        # Get last run time
        last_run = 'Never'
        if runs:
            last_run_time = runs[0].get('startedAt', '')
            if last_run_time:
                try:
                    dt = datetime.fromisoformat(last_run_time.replace('Z', '+00:00'))
                    last_run = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    last_run = last_run_time
        
        return {
            'status': status,
            'last_run': last_run,
            'success_rate': round(success_rate, 1),
            'avg_build_time': avg_build_time,
            'total_runs': len(runs),
            'successful_runs': successful_runs,
            'failed_runs': total_completed - successful_runs
        }
    
    def _calculate_duration(self, started_at: str, completed_at: str) -> str:
        """Calculate duration between start and completion times"""
        if not started_at or not completed_at:
            return 'N/A'
        
        try:
            start_dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            
            duration = end_dt - start_dt
            
            if duration.total_seconds() < 60:
                return f"{int(duration.total_seconds())}s"
            elif duration.total_seconds() < 3600:
                minutes = int(duration.total_seconds() // 60)
                seconds = int(duration.total_seconds() % 60)
                return f"{minutes}m {seconds}s"
            else:
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                return f"{hours}h {minutes}m"
                
        except Exception:
            return 'N/A'
    
    def _determine_trigger(self, run: Dict[str, any]) -> str:
        """Determine what triggered the workflow run"""
        # This is a simplified version - in practice, you'd need to analyze
        # the workflow trigger information more carefully
        return 'Push'  # Default assumption
    
    def get_performance_metrics(self) -> Dict[str, any]:
        """Get performance metrics for the CI/CD pipeline"""
        try:
            # Get runs from the last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            result = subprocess.run([
                'gh', 'run', 'list', '--limit', '100', '--json', 
                'status,conclusion,startedAt,completedAt'
            ], capture_output=True, text=True, check=True)
            
            runs = json.loads(result.stdout)
            
            # Filter runs from last 30 days
            recent_runs = [
                run for run in runs 
                if run.get('startedAt') and run['startedAt'] > thirty_days_ago
            ]
            
            # Calculate metrics
            total_runs = len(recent_runs)
            successful_runs = sum(1 for run in recent_runs if run.get('conclusion') == 'success')
            failed_runs = sum(1 for run in recent_runs if run.get('conclusion') == 'failure')
            cancelled_runs = sum(1 for run in recent_runs if run.get('conclusion') == 'cancelled')
            
            # Calculate build times
            build_times = []
            for run in recent_runs:
                if run.get('startedAt') and run.get('completedAt'):
                    duration = self._calculate_duration(run['startedAt'], run['completedAt'])
                    if duration != 'N/A':
                        try:
                            parts = duration.split()
                            minutes = 0
                            for part in parts:
                                if 'm' in part:
                                    minutes += int(part.replace('m', ''))
                                elif 's' in part:
                                    minutes += int(part.replace('s', '')) / 60
                            build_times.append(minutes)
                        except:
                            pass
            
            avg_build_time = sum(build_times) / len(build_times) if build_times else 0
            min_build_time = min(build_times) if build_times else 0
            max_build_time = max(build_times) if build_times else 0
            
            return {
                'period': 'Last 30 days',
                'total_runs': total_runs,
                'successful_runs': successful_runs,
                'failed_runs': failed_runs,
                'cancelled_runs': cancelled_runs,
                'success_rate': (successful_runs / total_runs * 100) if total_runs > 0 else 0,
                'failure_rate': (failed_runs / total_runs * 100) if total_runs > 0 else 0,
                'avg_build_time_minutes': round(avg_build_time, 1),
                'min_build_time_minutes': round(min_build_time, 1),
                'max_build_time_minutes': round(max_build_time, 1),
                'total_build_time_hours': round(sum(build_times) / 60, 1) if build_times else 0
            }
            
        except Exception as e:
            print(f"❌ Error getting performance metrics: {str(e)}")
            return {'error': str(e)}
