import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://adfaetbhaenzbazrikjn.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFkZmFldGJoYWVuemJhenJpa2puIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTMxNjEwNzAsImV4cCI6MjEwODczNzA3MH0.Uiz9fN_SYgMjPjnwevYag9IT18zCpXau8UMWJN5t-K0';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
