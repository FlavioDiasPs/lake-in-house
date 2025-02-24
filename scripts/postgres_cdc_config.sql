

--CREATING SLOT
SELECT pg_create_logical_replication_slot('debezium_slot', 'test_decoding');
--pgoutput is the default for debezium as it is binary and more performant
--SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput'); 

--CHECKING SLOT
SELECT * FROM pg_replication_slots;

--CONSUMING SLOT
SELECT * FROM pg_logical_slot_get_changes('debezium_slot', NULL, NULL);

SELECT * FROM pg_stat_wal_receiver;
SELECT * FROM pg_walfile_name_offset(pg_current_wal_lsn());
SELECT * FROM pg_publication;
SELECT * FROM pg_subscription;


select count(1) from deposit_sample_data
select * from deposit_sample_data order by event_timestamp desc limit 1000;
select * from event_sample_data order by event_timestamp desc limit 1000;
select * from user_level_sample_data order by event_timestamp desc limit 1000;
select * from withdrawals_sample_data order by event_timestamp desc limit 1000;