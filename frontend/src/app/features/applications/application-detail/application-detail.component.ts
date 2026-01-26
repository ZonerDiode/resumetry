import { Component, inject, OnInit, signal } from '@angular/core';

import { ActivatedRoute, Router } from '@angular/router';
import { JobApplicationService } from '../../../core/services/job-application.service';
import { JobApplication } from '../../../core/models/job-application.model';
import { ApplicationStatus } from '../../../core/models/application-status.enum';

@Component({
    selector: 'app-application-detail',
    imports: [],
    templateUrl: './application-detail.component.html',
    styleUrl: './application-detail.component.css'
})
export class ApplicationDetailComponent implements OnInit {
  private readonly service = inject(JobApplicationService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  application = signal<JobApplication | null>(null);
  isLoading = signal(true);
  error = signal<string | null>(null);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadApplication(id);
    }
  }

  loadApplication(id: string): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.service.getApplication(id).subscribe({
      next: (app) => {
        this.application.set(app);
        this.isLoading.set(false);
      },
      error: (err) => {
        this.error.set('Failed to load application details');
        this.isLoading.set(false);
        console.error(err);
      }
    });
  }

  onEdit(): void {
    const app = this.application();
    if (app) {
      this.router.navigate(['/applications', app.id, 'edit']);
    }
  }

  onBack(): void {
    this.router.navigate(['/applications']);
  }

  onDelete(): void {
    const app = this.application();
    if (app && confirm(`Delete application for ${app.company}?`)) {
      this.service.deleteApplication(app.id).subscribe({
        next: () => this.router.navigate(['/applications']),
        error: (err) => {
          alert('Failed to delete application');
          console.error(err);
        }
      });
    }
  }

  getStatusColor(status: ApplicationStatus): string {
    const colors: Record<ApplicationStatus, string> = {
      [ApplicationStatus.APPLIED]: '#2196f3',
      [ApplicationStatus.SCREEN]: '#ff9800',
      [ApplicationStatus.INTERVIEW]: '#9c27b0',
      [ApplicationStatus.OFFER]: '#4caf50',
      [ApplicationStatus.REJECTED]: '#f44336',
      [ApplicationStatus.WITHDRAWN]: '#757575',
      [ApplicationStatus.GHOSTED]: '#9e9e9e'
    };
    return colors[status];
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}
