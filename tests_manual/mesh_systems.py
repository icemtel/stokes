import mesh

system1 = {'sphere_1': 124}
system2 = {'sphere_2': 12414}
system3 = {'fL21': "safas"}

res = mesh.join_systems(system1, system2, system3)
print(res)

system22 = {'sphere_2': 124214}

res = mesh.join_systems(system1, system2, system22)
print(res)

