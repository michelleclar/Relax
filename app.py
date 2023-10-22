from core.base.execute import run, Build, ScriptArgs, Strategy, MatchRule, Policy
import commons.img_name as img_name
def main():
    a1 = ScriptArgs(task_name="式神录", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template(img_name.test_1))
    a2 = ScriptArgs(task_name="返回", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template(img_name.test_2))
    #
    # a3 = ScriptArgs(task_name="结算", strategy=ClickStrategy(Strategy.CENTER),
    #                 match_rule=MatchRule().template("settle"))
    # a4 = ScriptArgs(task_name="结束", strategy=ClickStrategy(Strategy.CENTER), match_rule=MatchRule().template("end"))
    build = Build()
    task = build.BuildTaskArgs("主账号")
    task.add_nodes({a1, a2})
    task.add_edge(a1, a2)
    task.build()

    run(build=build, script_tasks=[task])


if __name__ == '__main__':
    main()
