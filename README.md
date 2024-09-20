Uzelac Yvann PROJET 
# Documentation pour python 
```
        if loop==0 and self.name == "P1":
            #      self.broadcast("PMSG")
            #########
            # if loop==1 and self.name == "P2":
            #     self.sendTo("P1","P2 for P1")
            # if loop==2:
            # #########
            #     self.synchronization()
            # if loop==3 :
            #     self.broadcastSync()
            # #########
            # if loop==4 and self.name == "P2":
            #     self.sendToSync(3)
            # if loop==4 and self.name == "P3":
            #     self.recevFromSync(2)
```
## Différents tests
- Loop 0 -> Broadcast 
- Loop 1 -> Send to
- Loop 2 -> Synchronisation
- Loop 3 -> Broadcast sync
- Loop 4 -> SendToSync / RecevFromSync

## Autres
La numérotation a été faite, cependant elle n'impacte pas le code principal id != pid 
Il suffirait de quelques petites minutes pour l'implémenter dans tout le code principal mais pour des raisons de ne casser le code, j'ai préféré séparé ces deux parties



