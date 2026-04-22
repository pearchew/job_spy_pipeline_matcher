import React from 'react';
import { MapPin, Calendar, BarChart3, ExternalLink, ChevronRight } from 'lucide-react';
import { Job } from '../types';
import { cn } from '../lib/utils';

interface JobCardProps {
  job: Job;
  isSelected: boolean;
  onClick: () => void;
  onViewDescription: () => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, isSelected, onClick, onViewDescription }) => {
  const scoreColor = job.match_score >= 85 ? 'text-blue-600' : 
                    job.match_score >= 70 ? 'text-emerald-600' : 
                    'text-rose-500';

  return (
    <div 
      onClick={onClick}
      className={cn(
        "bg-white border rounded-lg p-4 shadow-sm transition-all cursor-pointer group flex flex-col",
        isSelected 
          ? "border-2 border-blue-500 ring-4 ring-blue-500/10" 
          : "border-slate-200 hover:border-slate-300"
      )}
    >
      <div className="flex justify-between items-start">
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-bold text-slate-800 leading-snug truncate group-hover:text-blue-600 transition-colors">
            {job.title}
          </h3>
          <div className="flex items-center space-x-3 mt-1.5 overflow-hidden">
            <span className="text-[11px] font-medium text-slate-500 flex items-center shrink-0">
              <MapPin className="w-3 h-3 mr-1 text-slate-400" />
              {job.location}
            </span>
            <span className="text-[11px] font-medium text-slate-400 shrink-0">|</span>
            <span className="text-[11px] font-medium text-slate-500 flex items-center truncate">
               {job.company}
            </span>
          </div>
        </div>
        <div className="flex flex-col items-end flex-shrink-0 ml-4">
          <div className={cn("text-xl font-mono font-black", scoreColor)}>
            {job.match_score}%
          </div>
          <div className="text-[9px] font-bold text-slate-400 uppercase tracking-tighter">Match Score</div>
        </div>
      </div>

      <div className="mt-4 flex space-x-2 border-t border-slate-50 pt-3">
        <button
          onClick={(e) => {
            e.stopPropagation();
            onViewDescription();
          }}
          className="flex-1 py-1.5 text-xs font-bold bg-slate-900 text-white rounded hover:bg-slate-800 transition-colors"
        >
          View Description
        </button>
        <a
          href={job.job_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          className="flex-1 py-1.5 text-center text-xs font-bold border border-slate-200 rounded text-slate-600 hover:bg-slate-50 transition-colors"
        >
          Apply Now <span className="opacity-40 ml-0.5 text-[10px]">↗</span>
        </a>
      </div>
    </div>
  );
};
