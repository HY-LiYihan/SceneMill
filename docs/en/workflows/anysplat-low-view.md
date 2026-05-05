# AnySplat Low-View Workflow

AnySplat is SceneMill's default backend for few-image inputs. It is meant to quickly produce an Isaac-loadable static visual background from one or a few images.

```bash
./scenemill run --preset auto --backend anysplat \
  --input /path/to/images \
  --workspace runs/anysplat_scene
```

## Artifacts

```text
runs/anysplat_scene/
  frames/images/
  anysplat/
    anysplat_manifest.yaml
    gaussians.ply
    camera_intrinsics.npy
    camera_intrinsics_pixels.npy
    camera_extrinsics.npy
  exports/
    scene_nurec_isaac.usdz
    scene_lightfield_isaac.usdz
  scene_manifest.yaml
```

## Camera And Coordinates

The AnySplat wrapper records crop metadata for the 448x448 network input, pixel intrinsics, and extrinsics. Downstream systems can use these fields to align an ego camera.

## Limits

- AnySplat produces a static visual background.
- Object interaction, collision, dynamic rigid bodies, and real-world scale are not solved by AnySplat alone.
- In `image2sim`, object pose, scale, and support relations remain handled by DA3, mask-depth optimization, and SceneGraph.
