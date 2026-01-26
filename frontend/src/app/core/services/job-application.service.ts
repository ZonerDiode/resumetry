import { Injectable, signal, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { JobApplication, JobApplicationCreate, JobApplicationUpdate } from '../models/job-application.model';

@Injectable({
  providedIn: 'root'
})
export class JobApplicationService {
  private readonly apiUrl = '/api/v1/applications';
  private readonly http = inject(HttpClient);

  // Signal-based cache for applications list
  private readonly applicationsSignal = signal<JobApplication[]>([]);
  public readonly applications = this.applicationsSignal.asReadonly();

  getApplications(): Observable<JobApplication[]> {
    return this.http.get<JobApplication[]>(this.apiUrl).pipe(
      tap(apps => this.applicationsSignal.set(apps))
    );
  }

  getApplication(id: string): Observable<JobApplication> {
    return this.http.get<JobApplication>(`${this.apiUrl}/${id}`);
  }

  createApplication(data: JobApplicationCreate): Observable<JobApplication> {
    return this.http.post<JobApplication>(this.apiUrl, data).pipe(
      tap(() => this.refreshCache())
    );
  }

  updateApplication(id: string, data: JobApplicationUpdate): Observable<JobApplication> {
    return this.http.patch<JobApplication>(`${this.apiUrl}/${id}`, data).pipe(
      tap(() => this.refreshCache())
    );
  }

  deleteApplication(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`).pipe(
      tap(() => this.refreshCache())
    );
  }

  refreshCache(): void {
    this.getApplications().subscribe();
  }
}
