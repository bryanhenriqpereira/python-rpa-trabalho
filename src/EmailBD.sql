create database EmailBD;
use EmailBD;

create table tb_email (
 ID int auto_increment primary key,
 remetente varchar(100),
 destinatario varchar (100),
 assunto varchar (225),
 conteudo text (1000),
 data_hr datetime,
 status_processamento varchar(10),
 filtragem varchar(100)
 );
 
 SELECT * from tb_email;
 
 insert into tb_email
(remetente, destinatario, assunto, conteudo, data_hr, status_processamento, filtragem)
 values
 ('Fulano','Maria','Trabalho',"Você está demitido",'07/10/26','OK','Trabalho');