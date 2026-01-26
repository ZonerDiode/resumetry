import { Component, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormArray, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { JobApplicationService } from '../../../core/services/job-application.service';
import { ApplicationStatus } from '../../../core/models/application-status.enum';

@Component({
  selector: 'app-application-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './application-form.component.html',
  styleUrl: './application-form.component.css'
})
export class ApplicationFormComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly service = inject(JobApplicationService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  isEditMode = false;
  applicationId: string | null = null;
  isSaving = false;

  readonly statusOptions = Object.values(ApplicationStatus);

  applicationForm = this.fb.group({
    company: ['', [Validators.required, Validators.maxLength(255)]],
    role: ['', [Validators.required, Validators.maxLength(255)]],
    description: [''],
    salary: ['', Validators.maxLength(100)],
    interestLevel: [2, [Validators.required, Validators.min(1), Validators.max(3)]],
    status: [ApplicationStatus.APPLIED, Validators.required],
    sourcePage: [''],
    reviewPage: [''],
    loginHints: [''],
    appliedDate: [this.todayString(), Validators.required],
    statusDate: [this.todayString(), Validators.required],
    notes: this.fb.array([])
  });

  get notesArray(): FormArray {
    return this.applicationForm.get('notes') as FormArray;
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEditMode = id !== null && id !== 'new';
    this.applicationId = id;

    if (this.isEditMode && id) {
      this.loadApplication(id);
    }
  }

  loadApplication(id: string): void {
    this.service.getApplication(id).subscribe({
      next: (app) => {
        this.applicationForm.patchValue({
          company: app.company,
          role: app.role,
          description: app.description,
          salary: app.salary,
          interestLevel: app.interestLevel,
          status: app.status,
          sourcePage: app.sourcePage,
          reviewPage: app.reviewPage,
          loginHints: app.loginHints,
          appliedDate: app.appliedDate,
          statusDate: app.statusDate
        });

        // Load notes
        app.notes.forEach(note => {
          this.notesArray.push(this.fb.group({
            occurDate: [note.occurDate, Validators.required],
            description: [note.description, Validators.required]
          }));
        });
      },
      error: (err) => {
        alert('Failed to load application');
        console.error(err);
        this.router.navigate(['/applications']);
      }
    });
  }

  addNote(): void {
    this.notesArray.push(this.fb.group({
      occurDate: [this.todayString(), Validators.required],
      description: ['', Validators.required]
    }));
  }

  removeNote(index: number): void {
    if (confirm('Remove this note?')) {
      this.notesArray.removeAt(index);
    }
  }

  onSave(): void {
    if (this.applicationForm.invalid) {
      this.applicationForm.markAllAsTouched();
      alert('Please fill in all required fields correctly');
      return;
    }

    this.isSaving = true;
    const formValue = this.applicationForm.value;

    if (this.isEditMode && this.applicationId) {
      // Update existing application
      this.service.updateApplication(this.applicationId, formValue as any).subscribe({
        next: (app) => {
          this.isSaving = false;
          this.router.navigate(['/applications', app.id]);
        },
        error: (err) => {
          this.isSaving = false;
          alert('Failed to update application');
          console.error(err);
        }
      });
    } else {
      // Create new application
      this.service.createApplication(formValue as any).subscribe({
        next: (app) => {
          this.isSaving = false;
          this.router.navigate(['/applications', app.id]);
        },
        error: (err) => {
          this.isSaving = false;
          alert('Failed to create application');
          console.error(err);
        }
      });
    }
  }

  onCancel(): void {
    if (this.isEditMode && this.applicationId) {
      this.router.navigate(['/applications', this.applicationId]);
    } else {
      this.router.navigate(['/applications']);
    }
  }

  private todayString(): string {
    return new Date().toISOString().split('T')[0];
  }

  isFieldInvalid(fieldName: string): boolean {
    const field = this.applicationForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}
