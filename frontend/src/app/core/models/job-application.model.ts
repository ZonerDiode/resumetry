import { ApplicationNote } from './application-note.model';
import { StatusItem } from './status-item.model';

export interface JobApplication {
  id: string;
  company: string;
  role: string;
  description: string;
  salary: string;
  topJob: boolean;
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
  topJob: boolean;
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
  topJob?: boolean;
  status?: StatusItem[];
  sourcePage?: string;
  reviewPage?: string;
  loginHints?: string;
  recruiterName?: string;
  recruiterCompany?: string;
  notes?: ApplicationNote[];
}
