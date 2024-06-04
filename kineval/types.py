from nptyping import NDArray, Shape, Float

Vec2 = NDArray[Shape["2"], Float]
Vec3 = NDArray[Shape["3"], Float]
Vec4 = NDArray[Shape["4"], Float]

Mat3D = NDArray[Shape["3, 3"], Float]
Mat4D = NDArray[Shape["4, 4"], Float]
