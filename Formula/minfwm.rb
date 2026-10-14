class Minfwm < Formula
  desc "Infinite 2D window canvas for macOS"
  homepage "https://github.com/snusxd/minfwm"
  url "https://github.com/snusxd/minfwm/archive/refs/tags/v1.1.tar.gz"
  version "1.1"
  sha256 "b6e3b0a398cc95775b1026a8b024eff18637d2adddc8a50384f2746b4a840967"
  license :cannot_represent # Upstream has not published a license.

  livecheck do
    url :stable
    strategy :github_latest
  end

  depends_on "cmake" => :build
  depends_on macos: :sonoma

  def install
    system "cmake", "-S", ".", "-B", "build", *std_cmake_args,
           "-DBUILD_TESTING=OFF", "-DCMAKE_OSX_DEPLOYMENT_TARGET=14.0"
    system "cmake", "--build", "build", "--target", "minfwm", "minfwmd", "--parallel"

    bin.install "build/minfwm", "build/minfwmd"
  end

  test do
    assert_match "minfwm", shell_output("#{bin}/minfwm version")
    assert_predicate bin/"minfwmd", :executable?
  end
end
