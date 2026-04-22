import React, { useState } from 'react';
import { ChevronDown, X, Check } from 'lucide-react';
import { cn } from '../lib/utils';

interface FilterBarProps {
  locations: string[];
  companies: string[];
  dates: string[];
  selectedLocations: string[];
  selectedCompanies: string[];
  selectedDates: string[];
  onToggleLocation: (loc: string) => void;
  onToggleCompany: (comp: string) => void;
  onToggleDate: (date: string) => void;
  onClearFilters: () => void;
}

const FilterDropdown: React.FC<{
  label: string;
  options: string[];
  selected: string[];
  onToggle: (val: string) => void;
  colorClass?: string;
}> = ({ label, options, selected, onToggle, colorClass = "blue" }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 rounded text-[11px] font-bold transition-all hover:border-slate-300",
          selected.length > 0 && "ring-1 ring-blue-500/20 border-blue-200 bg-blue-50/10"
        )}
      >
        <span className="text-slate-400 uppercase tracking-tighter">{label}:</span>
        <span className="text-slate-800">
          {selected.length === 0 ? "All" : selected.length === 1 ? selected[0] : `${selected.length} Selected`}
        </span>
        <ChevronDown className={cn("w-3 h-3 text-slate-400 transition-transform", isOpen && "rotate-180")} />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute top-full left-0 mt-1 w-56 max-h-64 overflow-y-auto bg-white border border-slate-200 rounded-md shadow-lg z-20 overflow-x-hidden">
            <div className="p-1">
              {options.length === 0 && <div className="p-2 text-[10px] text-slate-400 italic">No options available</div>}
              {options.map(option => (
                <button
                  key={option}
                  onClick={() => onToggle(option)}
                  className="w-full flex items-center justify-between px-3 py-1.5 text-left text-[11px] hover:bg-slate-50 transition-colors group"
                >
                  <span className={cn(
                    "truncate",
                    selected.includes(option) ? "text-blue-600 font-bold" : "text-slate-600"
                  )}>
                    {option}
                  </span>
                  {selected.includes(option) ? (
                    <Check className="w-3 h-3 text-blue-600" />
                  ) : (
                    <div className="w-3 h-3 border border-slate-200 rounded-sm group-hover:border-slate-300" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export const FilterBar: React.FC<FilterBarProps> = ({
  locations,
  companies,
  dates,
  selectedLocations,
  selectedCompanies,
  selectedDates,
  onToggleLocation,
  onToggleCompany,
  onToggleDate,
  onClearFilters
}) => {
  const totalActive = selectedLocations.length + selectedCompanies.length + selectedDates.length;

  return (
    <div className="flex flex-col bg-white border-b border-slate-200 shrink-0 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
      <div className="flex items-center px-6 py-2 pb-2.5 h-12 justify-between">
        <div className="flex items-center space-x-3">
          <FilterDropdown
            label="Location"
            options={locations}
            selected={selectedLocations}
            onToggle={onToggleLocation}
          />
          <FilterDropdown
            label="Company"
            options={companies}
            selected={selectedCompanies}
            onToggle={onToggleCompany}
          />
          <FilterDropdown
            label="Date"
            options={dates}
            selected={selectedDates}
            onToggle={onToggleDate}
          />

          {totalActive > 0 && (
            <button
              onClick={onClearFilters}
              className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-black uppercase tracking-widest text-rose-500 hover:text-rose-600 transition-colors"
            >
              <X className="w-3 h-3" />
              Reset filters
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
            <div className="text-[10px] text-slate-400 font-bold uppercase tracking-widest bg-slate-50 px-2 py-1 rounded border border-slate-100">
                Active: <span className="text-slate-900">{totalActive}</span>
            </div>
        </div>
      </div>

      {/* Active Filter Tags (Secondary Row) */}
      {totalActive > 0 && (
        <div className="px-6 pb-2 flex flex-wrap gap-2 animate-in fade-in slide-in-from-top-1 duration-200">
          {[
            ...selectedLocations.map(l => ({ val: l, type: 'Location', fn: onToggleLocation })),
            ...selectedCompanies.map(c => ({ val: c, type: 'Company', fn: onToggleCompany })),
            ...selectedDates.map(d => ({ val: d, type: 'Date', fn: onToggleDate })),
          ].map(({ val, type, fn }) => (
            <div 
              key={`${type}-${val}`}
              className="flex items-center gap-1.5 px-2 py-0.5 bg-slate-100 border border-slate-200 rounded text-[9px] font-bold text-slate-600 uppercase tracking-tight shadow-sm"
            >
              <span className="text-[8px] text-slate-400 opacity-70">{type}:</span>
              {val}
              <button 
                onClick={() => fn(val)}
                className="hover:text-rose-500 transition-colors"
              >
                <X className="w-2.5 h-2.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
