class Minfwm < Formula
  desc "Infinite 2D window canvas for macOS"
  homepage "https://github.com/snusxd/minfwm"
  url "https://github.com/snusxd/minfwm/archive/refs/tags/v1.2.tar.gz"
  version "1.2"
  sha256 "577dd415457534c15cfff2567c30ed2e112ff034cd390e433b3ad287c0573891"
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
