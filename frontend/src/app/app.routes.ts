import { Routes } from '@angular/router';
import { ApplicationListComponent } from './features/applications/application-list/application-list';
import { ApplicationDetailComponent } from './features/applications/application-detail/application-detail';
import { ApplicationFormComponent } from './features/applications/application-form/application-form';
import { SankeyReportComponent } from './features/reports/sankey-report/sankey-report';

export const routes: Routes = [
  { path: '', redirectTo: '/applications', pathMatch: 'full' },
  { path: 'applications', component: ApplicationListComponent },
  { path: 'applications/new', component: ApplicationFormComponent },
  { path: 'applications/:id', component: ApplicationDetailComponent },
  { path: 'applications/:id/edit', component: ApplicationFormComponent },
  { path: 'reports/sankey', component: SankeyReportComponent },
  { path: '**', redirectTo: '/applications' }
];
