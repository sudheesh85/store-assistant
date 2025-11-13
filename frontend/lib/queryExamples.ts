import { QueryExample } from '@/types';

export const queryExamples: QueryExample[] = [
  {
    id: '1',
    text: 'ഇന്ന് മൊത്തം വിൽപ്പന എത്ര?',
    category: 'Sales',
  },
  {
    id: '2',
    text: 'Top 5 products by revenue this week',
    category: 'Sales',
  },
  {
    id: '3',
    text: 'Which staff member sold the most items today?',
    category: 'Staff',
  },
  {
    id: '4',
    text: 'Show pending customer payments and amounts',
    category: 'Finance',
  },
  {
    id: '5',
    text: 'Stock levels for top 10 items',
    category: 'Inventory',
  },
  {
    id: '6',
    text: 'Average bill amount per customer today',
    category: 'Sales',
  },
  {
    id: '7',
    text: 'Monthly sales trend for the past 6 months',
    category: 'Sales',
  },
  {
    id: '8',
    text: 'Which products are low on stock (less than 10 units)?',
    category: 'Inventory',
  },
];

export const getExamplesByCategory = (category?: string): QueryExample[] => {
  if (!category) return queryExamples;
  return queryExamples.filter(ex => ex.category === category);
};

