import { Component, inject, OnInit } from '@angular/core';

import { ReactiveFormsModule, FormBuilder, FormArray, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { JobApplicationService } from '../../../core/services/job-application.service';
import { ApplicationStatus } from '../../../core/models/application-status.enum';
import { ContentEditableDirective } from '../../../core/directives/content-editable.directive';

@Component({
    selector: 'app-application-form',
    imports: [ReactiveFormsModule, ContentEditableDirective],
    templateUrl: './application-form.html',
    styleUrl: './application-form.css'
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
    topJob: [false],
    sourcePage: [''],
    reviewPage: [''],
    loginHints: [''],
    recruiterName: [''],
    recruiterCompany: [''],
    appliedDate: [this.todayString(), Validators.required],
    status: this.fb.array([]),
    notes: this.fb.array([])
  });

  get statusArray(): FormArray {
    return this.applicationForm.get('status') as FormArray;
  }

  get notesArray(): FormArray {
    return this.applicationForm.get('notes') as FormArray;
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.isEditMode = id !== null && id !== 'new';
    this.applicationId = id;

    if (this.isEditMode && id) {
      this.loadApplication(id);
    } else {
      // Auto-populate with APPLIED status for new applications
      this.addStatusItem(this.todayString(), ApplicationStatus.APPLIED);
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
          topJob: app.topJob,
          sourcePage: app.sourcePage,
          reviewPage: app.reviewPage,
          loginHints: app.loginHints,
          recruiterName: app.recruiterName,
          recruiterCompany: app.recruiterCompany,
          appliedDate: app.appliedDate
        });

        // Load status items
        app.status.forEach(item => {
          this.addStatusItem(item.occurDate, item.status);
        });
        this.sortFormArray(this.statusArray, 'occurDate');

        // Load notes
        app.notes.forEach(note => {
          this.notesArray.push(this.fb.group({
            occurDate: [note.occurDate, Validators.required],
            description: [note.description, Validators.required]
          }));
        });
        this.sortFormArray(this.notesArray, 'occurDate');
      },
      error: (err) => {
        alert('Failed to load application');
        console.error(err);
        this.router.navigate(['/applications']);
      }
    });
  }

  addStatusItem(occurDate?: string, status?: ApplicationStatus): void {
    this.statusArray.push(this.fb.group({
      occurDate: [occurDate ?? this.todayString(), Validators.required],
      status: [status ?? ApplicationStatus.APPLIED, Validators.required]
    }));
  }

  removeStatusItem(index: number): void {
    if (confirm('Remove this status entry?')) {
      this.statusArray.removeAt(index);
    }
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
    const d = new Date();
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  
  private sortFormArray(formArray: FormArray, field: string): void {
    const controls = formArray.controls.slice();
    controls.sort((a, b) => {
      const aVal = a.get(field)?.value ?? '';
      const bVal = b.get(field)?.value ?? '';
      return aVal.localeCompare(bVal);
    });
    
    formArray.clear();
    controls.forEach(c => formArray.push(c));
  }


  isFieldInvalid(fieldName: string): boolean {
    const field = this.applicationForm.get(fieldName);
    return !!(field && field.invalid && (field.dirty || field.touched));
  }
}
