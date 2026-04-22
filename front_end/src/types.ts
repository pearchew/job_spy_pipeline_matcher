export interface Job {
  processed_date: string;
  keyword: string;
  company: string;
  title: string;
  date_posted: string;
  match_score: number;
  matched_skills: string;
  gaps_in_skill: string;
  job_url: string;
  description: string;
  location: string;
  model_name?: string; // Added to track which model generated this data
}

export type TabType = 'board' | 'comparison';
