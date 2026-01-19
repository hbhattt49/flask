mkdir -p hello-scala/src/main/scala
cd hello-scala



cat > build.sbt <<'EOF'
ThisBuild / scalaVersion := "2.12.15"
ThisBuild / organization := "com.example"
ThisBuild / version := "0.1.0"

lazy val root = (project in file("."))
  .settings(
    name := "hello-scala"
  )
EOF



cat > src/main/scala/Main.scala <<'EOF'
object Main {
  def main(args: Array[String]): Unit = {
    val who = if (args.nonEmpty) args.mkString(" ") else "world"
    println(s"Hello, $who! Scala ${util.Properties.versionNumberString}")
  }
}
EOF



sbt clean compile
sbt run
# or pass args:
sbt "run Harshit"



sbt package
ls -l target/scala-2.12/*.jar



scala -cp target/scala-2.12/hello-scala_2.12-0.1.0.jar Main
