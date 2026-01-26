import { ApplicationStatus } from './application-status.enum';
import { ApplicationNote } from './application-note.model';

type JobApplicationInterestLevel = 1 | 2 | 3;

export interface JobApplication {
  id: string;
  company: string;
  role: string;
  description: string;
  salary: string;
  interestLevel: JobApplicationInterestLevel;
  status: ApplicationStatus;
  sourcePage: string;
  reviewPage: string;
  loginHints: string;
  appliedDate: string;
  statusDate: string;
  notes: ApplicationNote[];
}

export interface JobApplicationCreate {
  company: string;
  role: string;
  description?: string;
  salary?: string;
  interestLevel: JobApplicationInterestLevel;
  status?: ApplicationStatus;
  sourcePage?: string;
  reviewPage?: string;
  loginHints?: string;
  appliedDate?: string;
  statusDate?: string;
  notes?: ApplicationNote[];
}

export interface JobApplicationUpdate {
  company?: string;
  role?: string;
  description?: string;
  salary?: string;
  interestLevel?: JobApplicationInterestLevel;
  status?: ApplicationStatus;
  statusDate?: string;
  sourcePage?: string;
  reviewPage?: string;
  loginHints?: string;
  notes?: ApplicationNote[];
}
