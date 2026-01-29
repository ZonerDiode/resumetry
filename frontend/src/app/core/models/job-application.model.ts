import { ApplicationNote } from './application-note.model';
import { StatusItem } from './status-item.model';

type JobApplicationInterestLevel = 1 | 2 | 3;

export interface JobApplication {
  id: string;
  company: string;
  role: string;
  description: string;
  salary: string;
  interestLevel: JobApplicationInterestLevel;
  status: StatusItem[];
  sourcePage: string;
  reviewPage: string;
  loginHints: string;
  recruiterName: string;
  recruiterCompany: string;
  appliedDate: string;
  notes: ApplicationNote[];
}

export interface JobApplicationCreate {
  company: string;
  role: string;
  description?: string;
  salary?: string;
  interestLevel: JobApplicationInterestLevel;
  status?: StatusItem[];
  sourcePage?: string;
  reviewPage?: string;
  loginHints?: string;
  recruiterName?: string;
  recruiterCompany?: string;
  appliedDate?: string;
  notes?: ApplicationNote[];
}

export interface JobApplicationUpdate {
  company?: string;
  role?: string;
  description?: string;
  salary?: string;
  interestLevel?: JobApplicationInterestLevel;
  status?: StatusItem[];
  sourcePage?: string;
  reviewPage?: string;
  loginHints?: string;
  recruiterName?: string;
  recruiterCompany?: string;
  notes?: ApplicationNote[];
}
