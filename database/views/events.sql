drop view if exists	categorizing.events;

create view categorizing.events as														 

with a as
(
select sec,False as reversed,ch_to_sec_len(sec,ch-50) as s_ch,ch_to_sec_len(sec,ch) as e_ch,category from categorizing.jc
union
select sec,True as reversed,ch_to_sec_len(sec,ch+50) as s_ch,ch_to_sec_len(sec,ch) as e_ch,category from categorizing.jc
)
select *,int8range(least(s_ch,e_ch),greatest(s_ch,e_ch)) as r from a where s_ch!=e_ch;
