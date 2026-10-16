class Minfwm < Formula
  desc "Infinite 2D window canvas for macOS"
  homepage "https://github.com/snusxd/minfwm"
  url "https://github.com/snusxd/minfwm/archive/refs/tags/v1.3.tar.gz"
  version "1.3"
  sha256 "e3e680d938806fe74d06e4385fcd6a2a57aa0fabebf77d1d2f1d5b395d415d9b"
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
