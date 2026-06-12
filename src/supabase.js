import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'Insert URL';
const supabaseAnonKey = 'Insert Supabase Key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);