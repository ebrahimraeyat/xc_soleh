## A Design example of industrial steel structure with [XCFEM](https://github.com/xcfem/xc)
This is a structure with a span of 24 m for each frame, 72 m overall, modeling with non-prismitic elements.
for this, I divide columns and rafter with smaller pieces and assign IShape section to each piece.

![image](https://user-images.githubusercontent.com/8196112/113500090-7e029780-9530-11eb-95bb-e7d28d5a9ac2.png)


### view FEM model and Run analysis
For viewing FEM analysis run:
```python
python xc_model.py
```

For run complete analysis with all loads and combinations, execute:
```python
python xc_run_uls_checking
```

And for view the result, execute:
```python
python xc_display_uls_checking
```

![image](https://user-images.githubusercontent.com/8196112/113500207-5829c280-9531-11eb-96c3-ce89b80e71d3.png)

![image](https://user-images.githubusercontent.com/8196112/113500227-742d6400-9531-11eb-98a3-c75cba2637f9.png)
