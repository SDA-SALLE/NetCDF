#!/bin/bash

for f in $(find ../data/in/emis/rpm_sources/wear -type f -name \*.csv)
do
  python3 create_emis_halfhours_bc2014c.py ${f} -O
done

for f in $(find ../data/in/emis/rpm_sources/paved_roads -type f -name \*.csv)
do
  python3 create_emis_halfhours_bc2014c.py ${f} -O
done

for f in $(find ../data/in/emis/rpm_sources/quarrying -type f -name \*.csv)
do
  python3 create_emis_halfhours_bc2014c.py ${f} -O
done

for f in $(find ../data/in/emis/rpm_sources/road_bld_construction -type f -name \*.csv)
do
  python3 create_emis_halfhours_bc2014c.py ${f} -O
done

for f in $(find ../data/in/emis/rpm_sources/unpaved_roads -type f -name \*.csv)
do
  python3 create_emis_halfhours_bc2014c.py ${f} -O
done

