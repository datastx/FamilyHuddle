-- Family Huddle Database Schema
-- This creates all the tables needed for the football pool application

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Profiles table (allows multiple profiles per user)
CREATE TABLE IF NOT EXISTS profiles (
    profile_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    profile_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(user_id, profile_name)
);

-- NFL Seasons table
CREATE TABLE IF NOT EXISTS nfl_seasons (
    season_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    season_year INTEGER NOT NULL UNIQUE,
    regular_season_weeks INTEGER DEFAULT 18,
    is_current BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- NFL Teams table
CREATE TABLE IF NOT EXISTS nfl_teams (
    team_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_code VARCHAR(5) NOT NULL UNIQUE,
    team_name VARCHAR(50) NOT NULL,
    team_city VARCHAR(50) NOT NULL,
    conference VARCHAR(3) NOT NULL CHECK (conference IN ('AFC', 'NFC')),
    division VARCHAR(10) NOT NULL CHECK (division IN ('East', 'North', 'South', 'West')),
    points INTEGER DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- NFL Weeks table
CREATE TABLE IF NOT EXISTS nfl_weeks (
    week_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    season_id UUID NOT NULL REFERENCES nfl_seasons(season_id) ON DELETE CASCADE,
    week_number INTEGER NOT NULL,
    week_type VARCHAR(20) DEFAULT 'Regular',
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(season_id, week_number)
);

-- Pools table
CREATE TABLE IF NOT EXISTS pools (
    pool_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pool_name VARCHAR(100) NOT NULL,
    pool_description TEXT,
    created_by UUID NOT NULL REFERENCES users(user_id),
    season_year INTEGER NOT NULL,
    entry_fee DECIMAL(10,2) DEFAULT 0.00,
    max_participants INTEGER DEFAULT 20,
    registration_deadline TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Pool Participants table
CREATE TABLE IF NOT EXISTS pool_participants (
    participant_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pool_id UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    selections_complete BOOLEAN DEFAULT false,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(pool_id, profile_id)
);

-- Team Selections table
CREATE TABLE IF NOT EXISTS team_selections (
    selection_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pool_id UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    team_id UUID NOT NULL REFERENCES nfl_teams(team_id),
    selection_order INTEGER NOT NULL CHECK (selection_order BETWEEN 1 AND 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(pool_id, profile_id, team_id),
    UNIQUE(pool_id, profile_id, selection_order)
);

-- NFL Games table
CREATE TABLE IF NOT EXISTS nfl_games (
    game_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    week_id UUID NOT NULL REFERENCES nfl_weeks(week_id) ON DELETE CASCADE,
    home_team_id UUID NOT NULL REFERENCES nfl_teams(team_id),
    away_team_id UUID NOT NULL REFERENCES nfl_teams(team_id),
    game_date TIMESTAMP WITH TIME ZONE,
    home_score INTEGER,
    away_score INTEGER,
    game_status VARCHAR(20) DEFAULT 'SCHEDULED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Team Performance table
CREATE TABLE IF NOT EXISTS team_performance (
    performance_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    team_id UUID NOT NULL REFERENCES nfl_teams(team_id),
    season_id UUID NOT NULL REFERENCES nfl_seasons(season_id),
    games_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    win_percentage DECIMAL(5,3) DEFAULT 0.000,
    playoff_made BOOLEAN DEFAULT false,
    performance_score DECIMAL(10,3) DEFAULT 0.000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(team_id, season_id)
);

-- Pool Scores table
CREATE TABLE IF NOT EXISTS pool_scores (
    score_id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    pool_id UUID NOT NULL REFERENCES pools(pool_id) ON DELETE CASCADE,
    profile_id UUID NOT NULL REFERENCES profiles(profile_id) ON DELETE CASCADE,
    week_id UUID NOT NULL REFERENCES nfl_weeks(week_id),
    points_earned DECIMAL(10,2) DEFAULT 0.00,
    total_points DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    UNIQUE(pool_id, profile_id, week_id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_pool_participants_pool_id ON pool_participants(pool_id);
CREATE INDEX IF NOT EXISTS idx_pool_participants_profile_id ON pool_participants(profile_id);
CREATE INDEX IF NOT EXISTS idx_team_selections_pool_profile ON team_selections(pool_id, profile_id);
CREATE INDEX IF NOT EXISTS idx_nfl_games_week_id ON nfl_games(week_id);
CREATE INDEX IF NOT EXISTS idx_team_performance_season ON team_performance(season_id);
CREATE INDEX IF NOT EXISTS idx_pool_scores_pool_profile ON pool_scores(pool_id, profile_id);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE pools ENABLE ROW LEVEL SECURITY;
ALTER TABLE pool_participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_selections ENABLE ROW LEVEL SECURITY;
ALTER TABLE pool_scores ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (can be expanded later)
-- Allow service role to bypass RLS for admin operations
CREATE POLICY "Service role can manage users" ON users FOR ALL USING (auth.role() = 'service_role');
-- Allow authentication queries (needed for login)
CREATE POLICY "Allow authentication" ON users FOR SELECT USING (true);
CREATE POLICY "Users can update their own data" ON users FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Allow user registration" ON users FOR INSERT WITH CHECK (true);

CREATE POLICY "Service role can manage profiles" ON profiles FOR ALL USING (auth.role() = 'service_role');
-- Allow all authenticated operations on profiles (we handle auth in app layer)
CREATE POLICY "Allow profile operations" ON profiles FOR ALL USING (true);

-- Public read access for reference data
CREATE POLICY "Public read access" ON nfl_teams FOR SELECT USING (true);
CREATE POLICY "Public read access" ON nfl_seasons FOR SELECT USING (true);
CREATE POLICY "Public read access" ON nfl_weeks FOR SELECT USING (true);

-- Allow all operations on app tables (we handle auth in app layer)
CREATE POLICY "Allow pool operations" ON pools FOR ALL USING (true);
CREATE POLICY "Allow pool participant operations" ON pool_participants FOR ALL USING (true);
CREATE POLICY "Allow team selection operations" ON team_selections FOR ALL USING (true);
CREATE POLICY "Allow pool score operations" ON pool_scores FOR ALL USING (true);