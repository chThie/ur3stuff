### Pose

Vektor, der die Lage und Ausrichtung im Kartesischen Raum beschreibt.  
Kombination aus Positionsvektor (x,y,z) und Rotationsvektor (rx,ry,rz), der die Ausrichtung darstellt  
p[x, y, z, rx, ry, rz]


### moveJ
schneller  
führt Bewegungen aus, die im Gelenkraum des Roboters berechnet werden  
jedes Gelenk erreicht zum selben Zeitpunkt die gewünschte Stellung  
dadurch gekrümmte Bewegung  
Parameter: maximale Gelenkgeschwindigkeit (deg/s) und -beschleunigung (deg/s^2)

### moveL
lineare Bewegung zwischen Wegpunkten
jedes Gelenk führt komplexere Bewegungen aus, um gerade Bahn zu ermöglichen
Parameter: Werkzeuggeschwindigkeit (mm/s) und Werkzeugbeschleunigung(mm/s^2) und Merkmal(?)

### moveP
bewegt Werkzeug linear bei konstanter Geschwindigkeit und kreisrunden  Überblendbewegungen   
Überblendradius ist standardmäßig gemeinsamer Wert zwischen allen Wegpunkten  

### circleMove
kann zu moveP hinzugefügt werden, um Kreisbewegung zu bewirken  
bewegt sich über Zwischenpunkt zu Endpunkt in einer Kreisbahn  
Modus bestimmt wie sich das Werkzeug verhält:  
entweder fest oder uneingeschränkt (startpunkt geht in endpunkt über) 

