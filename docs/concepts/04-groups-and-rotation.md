# Groups and rotation

*Demonstrated by `CircleAndSquareRotating`, `CircleAndCircleRotating`,
`CircleAndCircleMoving`, and the flower scenes.*

## `VGroup`: many mobjects, one handle

A `VGroup` is a mobject whose children are other mobjects. Anything you do to
the group happens to all of them, and you still have the individual handles.

```python
circle = Circle(radius=1)
square = Square().rotate(PI/4).next_to(circle, DOWN, buff=0)

group = VGroup(circle, square)

self.play(Create(group), run_time=2)        # both appear at once
self.play(circle.animate.set_fill(GREEN, opacity=0.5))   # one member responds
```

`VGroup(circle, square)` and `VGroup(*[circle, square])` are the same call — the
latter is handy when building from a list.

`VGroup` also gives you structure operations that would otherwise be tedious:

| Call | Effect |
|:--|:--|
| `group.arrange(RIGHT, buff=0.5)` | lay the children out in a row |
| `group.arrange_in_grid(rows=2)` | …or in a grid |
| `group.set_color_by_gradient(RED, BLUE)` | colour the children along a gradient |
| `group[i]` | the i-th child (indexing works, including negative indices) |
| `group.add(sub)` / `group.remove(sub)` | grow/shrink the group at run time |

## `Rotate` needs an anchor

Rotation in the plane is defined by an angle **and a point**. Manim's default is
the mobject's own centre; `about_point` moves the pivot — and that single keyword
is the difference between "a rotation" and "an orbit".

```python
self.play(Rotate(group, angle=2*PI, about_point=ORIGIN, axis=OUT, run_time=5))
```

```python
self.play(Rotate(group, angle=2*PI, about_point=c2.get_center(), axis=OUT, run_time=5))
```

The first spins the group around the middle of the frame; the second makes the
two circles orbit each other, because the pivot is one of them.

`axis=OUT` is the z-axis (out of the screen) — rotations in Manim are 3-D
rotations about an axis, so `axis=RIGHT` would turn a flat shape in 3-D.

`Rotate` versus `mob.animate.rotate(angle)`:

| | Use |
|:--|:--|
| `Rotate(mob, angle=…, about_point=…)` | an *animation* — you choose duration, rate function, pivot |
| `mob.rotate(angle, about_point=…)` | an *instant* change (no animation) — ideal inside updaters |

## Moving: `shift` vs `move_to`

```python
group.shift(5 * LEFT)                  # relative: move by this vector
self.play(group.animate.move_to(5*RIGHT))   # absolute: centre on this point
```

Both work on groups, and both keep the group's internal layout. `shift` is for
"a bit further this way"; `move_to` is for "over there, exactly".

## Pitfalls

| Symptom | Cause | Fix |
|:--|:--|:--|
| the group rotates around the wrong point | `about_point` defaults to the mobject's centre | pass the pivot explicitly |
| the group "explodes" when rotated | you rotated the members individually rather than the group | rotate the group |
| `Create(group)` looks wrong | it draws all members simultaneously | `LaggedStartMap(Create, group)` for one-by-one |
| a member stops following the group | it was never added to the group | `group.add(mob)` (it must be a `VMobject`) |
| indexing surprises | `VGroup` indexing is by insertion order | `group[i]`, or keep named variables |

## Exercises

1. Make `CircleAndSquareRotating` spin around the square's centre instead.
2. Arrange three circles in a row with `arrange(RIGHT, buff=1)`, then rotate the row.
3. Give `CircleAndCircleRotating` a rotation of `4*PI` (two full turns).
4. In `FlowerWithColors`, wrap the petals in a `VGroup` and rotate *that*.
