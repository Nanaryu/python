select now();

select concat(imie, " ",nazwisko) as "imie nazwisko" from klient where nazwisko like "%ski";

select wartosc from zamowienie having max(wartosc);

select imie, nazwisko from klient 
inner join zamowienie on klient.id_klienta = zamowienie.id_zamowienia 
inner join towar on zamowienie.id_towaru = towar.id_towaru
where towar.id_towaru not in (1, 5, 8) 
group by klient.nazwisko asc;


select nazwa from towar inner join zamowienie on zamowienie.id_towaru = towar.id_towaru where zamowienie.id_klienta is null;

select * from zamowienie where date_sub(data_wyslania, interval 2 week) > data_zlozenia_zamowienia;

select towar.nazwa, sum(zamowienie.wartosc) as "laczna wartosc" from towar 
inner join zamowienie on towar.id_towaru = zamowienie.id_towaru group by towar.nazwa;

select imie, nazwisko from klient 
inner join zamowienie on klient.id_klienta = zamowienie.id_klienta group by klient.nazwisko desc having count(*)>10;

select * from klient inner join zamowienie on klient.id_klienta = zamowienie.id_zamowienia having zamowienie.wartosc = max(zamowienie.wartosc);

select nazwa from towar where month(data_produkcji) = month(now()) and year(data_produkcji) = year(now());

select imie, nazwisko from klient where year(data_urodzenia) + 18 = year(now());

select * from klient 
inner join zamowienie on klient.id_klienta = zamowienie.id_klienta where zamowienie.wartosc = (select max(wartosc) from zamowienie);
