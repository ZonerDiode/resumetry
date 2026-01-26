import { Routes } from '@angular/router';
import { ApplicationListComponent } from './features/applications/application-list/application-list.component';
import { ApplicationDetailComponent } from './features/applications/application-detail/application-detail.component';
import { ApplicationFormComponent } from './features/applications/application-form/application-form.component';

export const routes: Routes = [
  { path: '', redirectTo: '/applications', pathMatch: 'full' },
  { path: 'applications', component: ApplicationListComponent },
  { path: 'applications/new', component: ApplicationFormComponent },
  { path: 'applications/:id', component: ApplicationDetailComponent },
  { path: 'applications/:id/edit', component: ApplicationFormComponent },
  { path: '**', redirectTo: '/applications' }
];
