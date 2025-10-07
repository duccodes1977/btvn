from direct.showbase.ShowBase import ShowBase
from panda3d.core import DirectionalLight, AmbientLight, Vec4, WindowProperties, Vec3
from direct.task import Task
from panda3d.core import CardMaker
from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher
from panda3d.core import Plane, Point3, CollisionSphere, CollisionPlane

class MyGame(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()

        # --- Mặt trời ---
        self.sun = self.loader.loadModel("models/smiley")
        self.sun.reparentTo(self.render)
        self.sun.setScale(2)
        self.sun.setPos(50, 50, 80)
        self.sun.setColor(1, 1, 0.5, 1)

        # --- Cấu hình cửa sổ ---
        props = WindowProperties()
        props.setTitle("First-Person Camera Control")
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.setFrameRateMeter(True)

        # --- Ánh sáng ---
        dlight = DirectionalLight("dlight")
        dlight.setColor(Vec4(1, 1, 0.9, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)

        alight = AmbientLight("alight")
        alight.setColor(Vec4(0.3, 0.3, 0.3, 1))
        self.render.setLight(self.render.attachNewNode(alight))

        # --- Camera ---
        self.camera.setPos(0, -20, 3)
        self.camera.lookAt(0, 0, 0)

        # --- Mặt phẳng (sàn) ---
        cm = CardMaker("ground")
        cm.setFrame(-80, 80, -80, 80)
        plane = render.attachNewNode(cm.generate())
        plane.setHpr(0, -90, 0)
        plane.setPos(0, 0, 0)
        tex = loader.loadTexture("maps/envir-ground.jpg")
        plane.setTexture(tex)

        # --- Chuột ---
        self.heading = 0
        self.pitch = 0
        self.center_mouse()

        # --- Phím ---
        self.keys = {"w": False, "s": False, "a": False, "d": False,
                     "lcontrol": False, "space": False}
        for key in self.keys:
            self.accept(key, self.set_key, [key, True])
            self.accept(key + "-up", self.set_key, [key, False])

        # --- Hệ thống va chạm ---
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()

        floor_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        floor_col = CollisionNode("floor")
        floor_col.addSolid(CollisionPlane(floor_plane))
        self.render.attachNewNode(floor_col)

        camera_sphere = CollisionSphere(0, 0, 0, 1)
        camera_col = CollisionNode("camera")
        camera_col.addSolid(camera_sphere)
        camera_col_np = self.camera.attachNewNode(camera_col)

        self.pusher.addCollider(camera_col_np, self.camera)
        self.cTrav.addCollider(camera_col_np, self.pusher)

        # --- Trọng lực ---
        self.gravity = -0.02
        self.jump_strength = 0.5
        self.vertical_speed = 0
        self.on_ground = False

        # --- Task ---
        self.taskMgr.add(self.update_camera, "UpdateCameraTask")
        self.taskMgr.add(self.update_movement, "UpdateMovementTask")
        self.taskMgr.add(self.apply_gravity, "ApplyGravityTask")

        print("✅ Dùng chuột để xoay, giữ WASD để di chuyển, Ctrl để tăng tốc, Space để nhảy liên tục.")

    # --- Chuột ---
    def center_mouse(self):
        winX = self.win.getXSize() // 2
        winY = self.win.getYSize() // 2
        self.win.movePointer(0, winX, winY)

    def update_camera(self, task):
        if self.mouseWatcherNode.hasMouse():
            md = self.win.getPointer(0)
            x, y = md.getX(), md.getY()
            centerX, centerY = self.win.getXSize() // 2, self.win.getYSize() // 2
            dx, dy = x - centerX, y - centerY

            sensitivity = 0.2
            self.heading -= dx * sensitivity
            self.pitch -= dy * sensitivity
            self.pitch = max(-60, min(60, self.pitch))
            self.camera.setHpr(self.heading, self.pitch, 0)
            self.center_mouse()
        return Task.cont

    # --- Phím ---
    def set_key(self, key, value):
        self.keys[key] = value

    def update_movement(self, task):
        base_speed = 0.3
        speed = base_speed * (2 if self.keys["lcontrol"] else 1)

        direction = Vec3(0, 0, 0)
        if self.keys["w"]:
            direction += Vec3(0, speed, 0)
        if self.keys["s"]:
            direction += Vec3(0, -speed, 0)
        if self.keys["a"]:
            direction += Vec3(-speed, 0, 0)
        if self.keys["d"]:
            direction += Vec3(speed, 0, 0)

        self.camera.setPos(self.camera, direction)
        return Task.cont

    # --- Trọng lực và nhảy liên tục ---
    def apply_gravity(self, task):
        dt = globalClock.getDt()
        self.vertical_speed += self.gravity
        self.camera.setZ(self.camera.getZ() + self.vertical_speed)

        if self.camera.getZ() <= 1:
            self.camera.setZ(1)
            self.vertical_speed = 0
            self.on_ground = True

            # Nếu giữ Space → nhảy liên tục
            if self.keys["space"]:
                self.jump()
        else:
            self.on_ground = False

        return Task.cont

    def jump(self):
        if self.on_ground:
            self.vertical_speed = self.jump_strength
            self.on_ground = False

if __name__ == "__main__":
    app = MyGame()
    app.run()
