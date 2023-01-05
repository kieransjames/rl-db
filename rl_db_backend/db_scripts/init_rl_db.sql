use rl_db;
#init team tables

create table team_bios(
	team_name varchar(255) not null,
    region varchar(255) constraint region_valid check (region in ('APAC','EU','MENA','NA','OCE','SAM','SSA')),
    formation_date date,
    disband_date date,
    liquipedia_link varchar(255),
    primary key (team_name)
);

create table team_aliases(
	team_alias varchar(255) not null,
    team_name varchar(255) not null,
    primary key (team_alias),
    foreign key (team_name) references team_bios(team_name)
);

create table raw_team_data(
	team_alias varchar(255) not null,
    opponent_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias) references team_aliases(team_alias),
    foreign key (opponent_alias) references team_aliases(team_alias),
    game_date date,
    color varchar(255) constraint color_valid check (color in ('Orange','Blue')),
    opponent_color varchar(255),
    check (opponent_color in ('Orange','Blue')),
    
    win int, Game_duration float, possession_time float, Against_possession_time float, time_in_side float, Against_time_in_side float,
    shots int, shots_against int, goals int, goals_against int, saves int, Against_saves int, 
    assists int, Against_assists int, score int, Against_score int,
    
    bpm float, bcpm float, avg_amount float, amount_collected float, amount_stolen float, amount_collected_big float, amount_stolen_big float, amount_collected_small float, 
    amount_stolen_small float, count_collected_big float, count_stolen_big float, count_collected_small float, count_stolen_small float, amount_overfill float,
    amount_overfill_stolen float, amount_used_while_supersonic float, time_zero_boost float, time_full_boost float, time_boost_0_25 float, time_boost_25_50 float,
    time_boost_50_75 float, time_boost_75_100 float,
    total_distance float, time_supersonic_speed float, time_boost_speed float, time_slow_speed float, time_ground float, 
    time_low_air float, time_high_air float, time_powerslide float, count_powerslide float,
    time_defensive_third float, time_neutral_third float, time_offensive_third float, 
    time_defensive_half float, time_offensive_half float, time_behind_ball float, time_infront_ball float,
    inflicted int, taken int,
    Against_bpm  float, Against_bcpm  float, Against_avg_amount  float, Against_amount_collected  float, Against_amount_stolen  float,
    Against_amount_collected_big  float, Against_amount_stolen_big  float, Against_amount_collected_small  float, 
    Against_amount_stolen_small  float, Against_count_collected_big  float, Against_count_stolen_big  float, 
    Against_count_collected_small  float, Against_count_stolen_small  float, Against_amount_overfill  float,
    Against_amount_overfill_stolen  float, Against_amount_used_while_supersonic  float, Against_time_zero_boost  float,
    Against_time_full_boost  float, Against_time_boost_0_25  float, Against_time_boost_25_50  float,
    Against_time_boost_50_75  float, Against_time_boost_75_100  float,
    Against_total_distance  float, Against_time_supersonic_speed  float, Against_time_boost_speed  float, 
    Against_time_slow_speed  float, Against_time_ground  float, 
    Against_time_low_air  float, Against_time_high_air  float, Against_time_powerslide  float, Against_count_powerslide float,
    Against_time_defensive_third  float, Against_time_neutral_third  float, Against_time_offensive_third  float, 
    Against_time_defensive_half  float, Against_time_offensive_half  float, Against_time_behind_ball  float, Against_time_infront_ball float
);

create table team_meta_register(
	team_alias varchar(255) not null,
    opponent_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias) references team_aliases(team_alias),
    foreign key (opponent_alias) references team_aliases(team_alias),
    foreign key (team_alias,game_id) references raw_team_data(team_alias,game_id),
    game_date date,
    color varchar(255),
    check (color in ('Orange','Blue')),
    opponent_color varchar(255),
    check (opponent_color in ('Orange','Blue'))
);

create table team_base_stats(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
    win int, Game_duration float, possession_time float, Against_possession_time float, time_in_side float, Against_time_in_side float,
    shots int, shots_against int, goals int, goals_against int, saves int, Against_saves int, 
    assists int, Against_assists int, score int, Against_score int
);

create table team_boost_stats_for(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
    bpm float, bcpm float, avg_amount float, amount_collected float, amount_stolen float, amount_collected_big float, amount_stolen_big float, amount_collected_small float, 
    amount_stolen_small float, count_collected_big float, count_stolen_big float, count_collected_small float, count_stolen_small float, amount_overfill float,
    amount_overfill_stolen float, amount_used_while_supersonic float, time_zero_boost float, time_full_boost float, time_boost_0_25 float, time_boost_25_50 float,
    time_boost_50_75 float, time_boost_75_100 float
);

create table team_movement_stats_for(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
    total_distance float, time_supersonic_speed float, time_boost_speed float, time_slow_speed float, time_ground float, 
    time_low_air float, time_high_air float, time_powerslide float, count_powerslide float
);

create table team_positioning_stats_for(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
    time_defensive_third float, time_neutral_third float, time_offensive_third float, 
    time_defensive_half float, time_offensive_half float, time_behind_ball float, time_infront_ball float
);

create table team_demo_stats(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
	inflicted int, taken int
);

create table team_boost_stats_against(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
	Against_bpm  float, Against_bcpm  float, Against_avg_amount  float, Against_amount_collected  float, Against_amount_stolen  float,
    Against_amount_collected_big  float, Against_amount_stolen_big  float, Against_amount_collected_small  float, 
    Against_amount_stolen_small  float, Against_count_collected_big  float, Against_count_stolen_big  float, 
    Against_count_collected_small  float, Against_count_stolen_small  float, Against_amount_overfill  float,
    Against_amount_overfill_stolen  float, Against_amount_used_while_supersonic  float, Against_time_zero_boost  float,
    Against_time_full_boost  float, Against_time_boost_0_25  float, Against_time_boost_25_50  float,
    Against_time_boost_50_75  float, Against_time_boost_75_100  float
);

create table team_movement_stats_against(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
	Against_total_distance  float, Against_time_supersonic_speed  float, Against_time_boost_speed  float, 
    Against_time_slow_speed  float, Against_time_ground  float, 
    Against_time_low_air  float, Against_time_high_air  float, Against_time_powerslide  float, Against_count_powerslide float
);

create table team_positioning_stats_against(
	team_alias varchar(255) not null,
    game_id varchar(255) not null,
    primary key (team_alias, game_id),
    foreign key (team_alias,game_id) references team_meta_register(team_alias,game_id),
    
	Against_time_defensive_third  float, Against_time_neutral_third  float, Against_time_offensive_third  float, 
    Against_time_defensive_half  float, Against_time_offensive_half  float, Against_time_behind_ball  float, Against_time_infront_ball float
);

delimiter $$
create trigger after_raw_team_insert
	after insert on raw_team_data for each row
    begin
		insert into team_meta_register (team_alias,opponent_alias,game_id,game_date,color,opponent_color)
        values (new.team_alias,new.opponent_alias,new.game_id,new.game_date,new.color,new.opponent_color);
        
        insert into team_base_stats (team_alias,game_id, win, Game_duration, possession_time, Against_possession_time, time_in_side, Against_time_in_side, 
									 shots, shots_against, goals, goals_against, saves, Against_saves, assists, Against_assists, score,Against_score)
		values (new.team_alias,new.game_id, new.win, new.Game_duration, new.possession_time, new.Against_possession_time, new.time_in_side, new.Against_time_in_side, 
				new.shots, new.shots_against, new.goals, new.goals_against, new.saves, new.Against_saves, new.assists, new.Against_assists, new.score,new.Against_score);
                
		insert into team_boost_stats_for (team_alias, game_id, bpm, bcpm, avg_amount, amount_collected, amount_stolen, amount_collected_big, amount_stolen_big, amount_collected_small, 
										  amount_stolen_small, count_collected_big, count_stolen_big, count_collected_small, count_stolen_small, amount_overfill,
										  amount_overfill_stolen, amount_used_while_supersonic, time_zero_boost, time_full_boost, time_boost_0_25, time_boost_25_50, time_boost_50_75, time_boost_75_100)
		values (new.team_alias, new.game_id, new.bpm, new.bcpm, new.avg_amount, new.amount_collected, new.amount_stolen, new.amount_collected_big, new.amount_stolen_big, new.amount_collected_small, 
				new.amount_stolen_small, new.count_collected_big, new.count_stolen_big, new.count_collected_small, new.count_stolen_small, new.amount_overfill,
				new.amount_overfill_stolen, new.amount_used_while_supersonic, new.time_zero_boost, new.time_full_boost, 
                new.time_boost_0_25, new.time_boost_25_50, new.time_boost_50_75, new.time_boost_75_100);
        
        insert into team_movement_stats_for (team_alias, game_id, total_distance, time_supersonic_speed, time_boost_speed, time_slow_speed, time_ground, 
											 time_low_air, time_high_air, time_powerslide, count_powerslide)
		values (new.team_alias, new.game_id, new.total_distance, new.time_supersonic_speed, new.time_boost_speed, new.time_slow_speed, new.time_ground, 
											 new.time_low_air, new.time_high_air, new.time_powerslide, new.count_powerslide);
                
		insert into team_positioning_stats_for (team_alias,game_id, time_defensive_third, time_neutral_third, time_offensive_third, 
												time_defensive_half, time_offensive_half, time_behind_ball, time_infront_ball)
		values (new.team_alias, new.game_id, new.time_defensive_third, new.time_neutral_third, new.time_offensive_third, 
												new.time_defensive_half, new.time_offensive_half, new.time_behind_ball, new.time_infront_ball);
        
		insert into team_demo_stats (team_alias,game_id, inflicted, taken)
		values (new.team_alias, new.game_id, new.inflicted, new.taken);
        
		insert into team_boost_stats_against (team_alias,game_id, Against_bpm , Against_bcpm , Against_avg_amount , Against_amount_collected , Against_amount_stolen ,
												Against_amount_collected_big , Against_amount_stolen_big , Against_amount_collected_small , 
												Against_amount_stolen_small , Against_count_collected_big , Against_count_stolen_big , 
												Against_count_collected_small , Against_count_stolen_small , Against_amount_overfill ,
												Against_amount_overfill_stolen , Against_amount_used_while_supersonic , Against_time_zero_boost ,
												Against_time_full_boost , Against_time_boost_0_25 , Against_time_boost_25_50 ,
												Against_time_boost_50_75 , Against_time_boost_75_100 )
		values (new.team_alias,new.game_id, new.Against_bpm , new.Against_bcpm , new.Against_avg_amount , new.Against_amount_collected , new.Against_amount_stolen ,
												new.Against_amount_collected_big , new.Against_amount_stolen_big , new.Against_amount_collected_small , 
												new.Against_amount_stolen_small , new.Against_count_collected_big , new.Against_count_stolen_big , 
												new.Against_count_collected_small , new.Against_count_stolen_small , new.Against_amount_overfill ,
												new.Against_amount_overfill_stolen , new.Against_amount_used_while_supersonic , new.Against_time_zero_boost ,
												new.Against_time_full_boost , new.Against_time_boost_0_25 , new.Against_time_boost_25_50 ,
												new.Against_time_boost_50_75 , new.Against_time_boost_75_100 );       
  
		insert into team_movement_stats_against (team_alias,game_id, Against_total_distance , Against_time_supersonic_speed , Against_time_boost_speed , 
													Against_time_slow_speed , Against_time_ground , 
													Against_time_low_air , Against_time_high_air , Against_time_powerslide , Against_count_powerslide)
		values (new.team_alias,new.game_id, new.Against_total_distance , new.Against_time_supersonic_speed , new.Against_time_boost_speed , 
				new.Against_time_slow_speed , new.Against_time_ground , 
				new.Against_time_low_air , new.Against_time_high_air , new.Against_time_powerslide , new.Against_count_powerslide);
		
		insert into team_positioning_stats_against (team_alias,game_id, Against_time_defensive_third , Against_time_neutral_third , Against_time_offensive_third , 
													Against_time_defensive_half , Against_time_offensive_half , Against_time_behind_ball , Against_time_infront_ball)
		values (new.team_alias, new.game_id, new.Against_time_defensive_third , new.Against_time_neutral_third , new.Against_time_offensive_third , 
				new.Against_time_defensive_half , new.Against_time_offensive_half , new.Against_time_behind_ball , new.Against_time_infront_ball);       
		end;	
$$
delimiter ;

#init player tables

create table player_ids(
	player_id varchar(255),
    player_name varchar(255),
    primary key (player_id),
    platform varchar(255)
);

create table raw_player_data(
	player_id varchar(255),
    game_id varchar(255),
    player_name varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id) references player_ids(player_id),
    
    team_alias varchar(255),
    foreign key (team_alias) references team_aliases(team_alias),
    opponent_alias varchar(255),
    foreign key (opponent_alias) references team_aliases(team_alias),
    
    game_date date,
    color varchar(255),
    check (color in ('Orange','Blue')),
    
    platform varchar(255),
    
    Game_duration float, shots int, shots_against int, goals int, goals_against int, saves int, assists int, score int,
	mvp int, shooting_percentage float, bpm float, bcpm float, avg_amount float,
	amount_collected float, amount_stolen float, amount_collected_big float,
	amount_stolen_big float, amount_collected_small float, amount_stolen_small float,
	count_collected_big float, count_stolen_big float, count_collected_small float,
	count_stolen_small float, amount_overfill float, amount_overfill_stolen float,
	amount_used_while_supersonic float, time_zero_boost float, percent_zero_boost float,
	time_full_boost float, percent_full_boost float, time_boost_0_25 float,
	time_boost_25_50 float, time_boost_50_75 float, time_boost_75_100 float,
	percent_boost_0_25 float, percent_boost_25_50 float, percent_boost_50_75 float,
	percent_boost_75_100 float, avg_speed float, total_distance float,
	time_supersonic_speed float, time_boost_speed float, time_slow_speed float,
	time_ground float, time_low_air float, time_high_air float, time_powerslide float,
	count_powerslide float, avg_powerslide_duration float, avg_speed_percentage float,
	percent_slow_speed float, percent_boost_speed float, percent_supersonic_speed float,
	percent_ground float, percent_low_air float, percent_high_air float,
	avg_distance_to_ball float, avg_distance_to_ball_possession float,
	avg_distance_to_ball_no_possession float, avg_distance_to_mates float,
	time_defensive_third float, time_neutral_third float, time_offensive_third float,
	time_defensive_half float, time_offensive_half float, time_behind_ball float,
	time_infront_ball float, time_most_back float, time_most_forward float,
	time_closest_to_ball float, time_farthest_from_ball float,
	percent_defensive_third float, percent_offensive_third float,
	percent_neutral_third float, percent_defensive_half float,
	percent_offensive_half float, percent_behind_ball float, percent_infront_ball float,
	percent_most_back float, percent_most_forward float, percent_closest_to_ball float,
	percent_farthest_from_ball float, inflicted float, taken float
);

create table player_meta_register(
	player_id varchar(255) not null,
    game_id varchar(255) not null,
	foreign key (player_id,game_id) references raw_player_data(player_id,game_id),
    primary key (player_id, game_id),
    foreign key (player_id) references player_ids(player_id),

    
	team_alias varchar(255),
    foreign key (team_alias) references team_aliases(team_alias),
    opponent_alias varchar(255),
    foreign key (opponent_alias) references team_aliases(team_alias),

	platform varchar(255),
    
    game_date date,
    color varchar(255),
    check (color in ('Orange','Blue'))
);

create table player_base_stats(
	player_id varchar(255),
    game_id varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id,game_id) references raw_player_data(player_id,game_id),
    
	Game_duration float, shots int, shots_against int, goals int, goals_against int, saves int, assists int, score int,
	mvp int, shooting_percentage float
);

create table player_boost_stats(
	player_id varchar(255),
    game_id varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id,game_id) references raw_player_data(player_id,game_id),
    
	bpm float, bcpm float, avg_amount float,
	amount_collected float, amount_stolen float, amount_collected_big float,
	amount_stolen_big float, amount_collected_small float, amount_stolen_small float,
	count_collected_big float, count_stolen_big float, count_collected_small float,
	count_stolen_small float, amount_overfill float, amount_overfill_stolen float,
	amount_used_while_supersonic float, time_zero_boost float, percent_zero_boost float,
	time_full_boost float, percent_full_boost float, time_boost_0_25 float,
	time_boost_25_50 float, time_boost_50_75 float, time_boost_75_100 float,
	percent_boost_0_25 float, percent_boost_25_50 float, percent_boost_50_75 float,
	percent_boost_75_100 float
);

create table player_movement_stats(
	player_id varchar(255),
    game_id varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id,game_id) references raw_player_data(player_id,game_id),
    
	avg_speed float, total_distance float,
	time_supersonic_speed float, time_boost_speed float, time_slow_speed float,
	time_ground float, time_low_air float, time_high_air float, time_powerslide float,
	count_powerslide float, avg_powerslide_duration float, avg_speed_percentage float,
	percent_slow_speed float, percent_boost_speed float, percent_supersonic_speed float,
    percent_ground float, percent_low_air float, percent_high_air float
);

create table player_positioning_stats(
	player_id varchar(255),
    game_id varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id,game_id) references raw_player_data(player_id,game_id),
    
	avg_distance_to_ball float, avg_distance_to_ball_possession float,
	avg_distance_to_ball_no_possession float, avg_distance_to_mates float,
	time_defensive_third float, time_neutral_third float, time_offensive_third float,
	time_defensive_half float, time_offensive_half float, time_behind_ball float,
	time_infront_ball float, time_most_back float, time_most_forward float,
	time_closest_to_ball float, time_farthest_from_ball float,
	percent_defensive_third float, percent_offensive_third float,
	percent_neutral_third float, percent_defensive_half float,
	percent_offensive_half float, percent_behind_ball float, percent_infront_ball float,
	percent_most_back float, percent_most_forward float, percent_closest_to_ball float,
	percent_farthest_from_ball float
);

create table player_demo_stats(
	player_id varchar(255),
    game_id varchar(255),
    primary key (player_id,game_id),
    foreign key (player_id,game_id) references raw_player_data(player_id,game_id),	
    
    inflicted float, taken float
);



delimiter $$
create trigger after_raw_player_insert
	after insert on raw_player_data for each row
    begin
		insert into player_meta_register (player_id,game_id,team_alias,opponent_alias,platform,game_date,color)
        values (new.player_id,new.game_id,new.team_alias,new.opponent_alias,new.platform,new.game_date,new.color);
        
        insert into player_base_stats (player_id,game_id,Game_duration, shots, shots_against, goals, goals_against, saves, assists, score,
									   mvp, shooting_percentage)
        values (new.player_id,new.game_id,new.Game_duration, new.shots, new.shots_against, new.goals, new.goals_against, new.saves, new.assists, new.score,
									   new.mvp, new.shooting_percentage);
        
        insert into player_boost_stats (player_id,game_id,bpm, bcpm, avg_amount,
										amount_collected, amount_stolen, amount_collected_big,
										amount_stolen_big, amount_collected_small, amount_stolen_small,
										count_collected_big, count_stolen_big, count_collected_small,
										count_stolen_small, amount_overfill, amount_overfill_stolen,
										amount_used_while_supersonic, time_zero_boost, percent_zero_boost,
										time_full_boost, percent_full_boost, time_boost_0_25,
										time_boost_25_50, time_boost_50_75, time_boost_75_100,
										percent_boost_0_25, percent_boost_25_50, percent_boost_50_75,
										percent_boost_75_100)
        values (new.player_id,new.game_id,new.bpm, new.bcpm, new.avg_amount,
										new.amount_collected, new.amount_stolen, new.amount_collected_big,
										new.amount_stolen_big, new.amount_collected_small, new.amount_stolen_small,
										new.count_collected_big, new.count_stolen_big, new.count_collected_small,
										new.count_stolen_small, new.amount_overfill, new.amount_overfill_stolen,
										new.amount_used_while_supersonic, new.time_zero_boost, new.percent_zero_boost,
										new.time_full_boost, new.percent_full_boost, new.time_boost_0_25,
										new.time_boost_25_50, new.time_boost_50_75, new.time_boost_75_100,
										new.percent_boost_0_25, new.percent_boost_25_50, new.percent_boost_50_75,
										new.percent_boost_75_100);
        
        insert into player_movement_stats (player_id,game_id, avg_speed, total_distance,
											time_supersonic_speed, time_boost_speed, time_slow_speed,
											time_ground, time_low_air, time_high_air, time_powerslide,
											count_powerslide, avg_powerslide_duration, avg_speed_percentage,
											percent_slow_speed, percent_boost_speed, percent_supersonic_speed,
											percent_ground, percent_low_air, percent_high_air)
        values (new.player_id,new.game_id,new.avg_speed, new.total_distance,
											new.time_supersonic_speed, new.time_boost_speed, new.time_slow_speed,
											new.time_ground, new.time_low_air, new.time_high_air, new.time_powerslide,
											new.count_powerslide, new.avg_powerslide_duration, new.avg_speed_percentage,
											new.percent_slow_speed, new.percent_boost_speed, new.percent_supersonic_speed,
											new.percent_ground, new.percent_low_air, new.percent_high_air);
        
        insert into player_positioning_stats (player_id,game_id, avg_distance_to_ball, avg_distance_to_ball_possession,
												avg_distance_to_ball_no_possession, avg_distance_to_mates,
												time_defensive_third, time_neutral_third, time_offensive_third,
												time_defensive_half, time_offensive_half, time_behind_ball,
												time_infront_ball, time_most_back, time_most_forward,
												time_closest_to_ball, time_farthest_from_ball,
												percent_defensive_third, percent_offensive_third,
												percent_neutral_third, percent_defensive_half,
												percent_offensive_half, percent_behind_ball, percent_infront_ball,
												percent_most_back, percent_most_forward, percent_closest_to_ball,
												percent_farthest_from_ball)
        values (new.player_id,new.game_id,new.avg_distance_to_ball, new.avg_distance_to_ball_possession,
												new.avg_distance_to_ball_no_possession, new.avg_distance_to_mates,
												new.time_defensive_third, new.time_neutral_third, new.time_offensive_third,
												new.time_defensive_half, new.time_offensive_half, new.time_behind_ball,
												new.time_infront_ball, new.time_most_back, new.time_most_forward,
												new.time_closest_to_ball, new.time_farthest_from_ball,
												new.percent_defensive_third, new.percent_offensive_third,
												new.percent_neutral_third, new.percent_defensive_half,
												new.percent_offensive_half, new.percent_behind_ball, new.percent_infront_ball,
												new.percent_most_back, new.percent_most_forward, new.percent_closest_to_ball,
												new.percent_farthest_from_ball);
        
        insert into player_demo_stats (player_id,game_id,inflicted, taken)
        values (new.player_id,new.game_id,new.inflicted, new.taken);
		end;	
$$
delimiter ;




