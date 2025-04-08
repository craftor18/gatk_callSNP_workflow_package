from gatk_snp_pipeline.dependency_checker import DependencyChecker
import argparse

def main():
    parser = argparse.ArgumentParser(description="测试依赖检查功能")
    parser.add_argument("--skip-version-check", action="store_true", 
                      help="跳过版本检查，只检查软件是否存在")
    args = parser.parse_args()
    
    checker = DependencyChecker(skip_version_check=args.skip_version_check)
    print("开始检查依赖...")
    
    if args.skip_version_check:
        print("已启用版本检查跳过，仅检查软件是否存在")
    
    checker.check_all()
    
    if checker.has_errors():
        print("发现以下问题：")
        for error in checker.get_errors():
            print(f"- {error}")
    else:
        print("所有依赖检查通过！")

if __name__ == "__main__":
    main() 