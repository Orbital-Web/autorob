from nptyping import NDArray, Shape, Float

Vec = NDArray[Shape["N"], Float]  # (N,) vector
Vec2 = NDArray[Shape["2"], Float]  # (2,) vector
Vec3 = NDArray[Shape["3"], Float]  # (3,) vector
Vec4 = NDArray[Shape["4"], Float]  # (4,) vector

Mat2 = NDArray[Shape["2, 2"], Float]  # (2, 2) matrix
Mat3 = NDArray[Shape["3, 3"], Float]  # (3, 3) matrix
Mat4 = NDArray[Shape["4, 4"], Float]  # (4, 4) matrix
