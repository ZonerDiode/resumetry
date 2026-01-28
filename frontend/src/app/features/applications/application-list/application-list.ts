import { Component, inject, OnInit, signal, computed } from '@angular/core';

import { Router } from '@angular/router';
import { JobApplicationService } from '../../../core/services/job-application.service';
import { JobApplication } from '../../../core/models/job-application.model';
import { ApplicationStatus } from '../../../core/models/application-status.enum';
import { StatusItem } from '../../../core/models/status-item.model';

@Component({
    selector: 'app-application-list',
    imports: [],
    templateUrl: './application-list.html',
    styleUrl: './application-list.css'
})
export class ApplicationListComponent implements OnInit {
  private readonly service = inject(JobApplicationService);
  private readonly router = inject(Router);

  filterText = signal('');
  viewMode = signal<'card' | 'table'>('table');
  isLoading = signal(true);
  error = signal<string | null>(null);

  // Computed signal for filtered & sorted applications
  displayedApplications = computed(() => {
    let apps = this.service.applications();

    // Filter by company
    const filter = this.filterText().toLowerCase();
    if (filter) {
      apps = apps.filter(app => app.company.toLowerCase().includes(filter));
    }

    // Sort by appliedDate (newest first)
    apps = [...apps].sort((a, b) =>
      new Date(b.appliedDate).getTime() - new Date(a.appliedDate).getTime()
    );

    return apps;
  });

  ngOnInit(): void {
    this.loadApplications();
  }

  loadApplications(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.service.getApplications().subscribe({
      next: () => this.isLoading.set(false),
      error: (err) => {
        this.error.set('Failed to load applications');
        this.isLoading.set(false);
        console.error(err);
      }
    });
  }

  onSelectApplication(app: JobApplication): void {
    this.router.navigate(['/applications', app.id]);
  }

  onCreateNew(): void {
    this.router.navigate(['/applications/new']);
  }

  onFilterChange(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.filterText.set(input.value);
  }

  getLatestStatus(app: JobApplication): StatusItem | null {
    if (app.status.length === 0) return null;
    return [...app.status].sort((a, b) =>
      new Date(b.occurDate).getTime() - new Date(a.occurDate).getTime()
    )[0];
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

  getInterestColor(level: number): string {
    return level === 3 ? '#4caf50' : level === 2 ? '#ff9800' : '#9e9e9e';
  }

  formatDate(dateString: string): string {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  }
}
