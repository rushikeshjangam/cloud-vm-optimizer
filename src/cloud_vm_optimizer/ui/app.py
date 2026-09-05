"""Browser-first dashboard for the complete Milestone A workflow."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from cloud_vm_optimizer.aws.ec2_service import EC2DemoService
from cloud_vm_optimizer.data.loader import load_vm_catalog, load_workload
from cloud_vm_optimizer.domain.models import AllocationResult
from cloud_vm_optimizer.services.optimization_service import (
    forecast_result_to_frame,
    optimize_forecast,
    run_forecast,
)


def _allocation_table(result: AllocationResult) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Measure": [
                "VM allocation",
                "Number of VMs",
                "Total vCPUs",
                "Total RAM (GB)",
                "Job capacity",
                "Operational cost (USD)",
                "Estimated energy (kWh)",
                "Utilization factor",
            ],
            "Value": [
                ", ".join(f"{name} x {count}" for name, count in result.vm_counts.items()),
                str(result.total_vms),
                f"{result.total_vcpus:.1f}",
                f"{result.total_memory_gb:.1f}",
                f"{result.total_job_capacity:.0f}",
                f"${result.cost_usd:.3f}",
                f"{result.energy_kwh:.3f}",
                f"{result.utilization_factor:.1%}",
            ],
        }
    )


def _show_aws_demo() -> None:
    st.header("8. AWS Demonstration")
    service = EC2DemoService.from_environment()
    if not service.enabled:
        st.info(
            "AWS demo mode disabled. The forecasting and optimization demo is fully "
            "functional and no AWS API call has been made."
        )
        st.code("AWS_DEMO_ENABLED=false", language="text")
        return

    st.warning(
        f"Read-only AWS demo mode is enabled in {service.region}. Only instances with "
        "all three required project tags are listed."
    )
    if st.button("Inspect tagged EC2 demo instances"):
        try:
            instances = service.list_demo_instances()
            if instances:
                st.dataframe(pd.DataFrame([item.__dict__ for item in instances]), hide_index=True)
            else:
                st.info("No matching tagged instances were found.")
        except Exception as error:  # The core demo should survive missing AWS access.
            st.error(f"AWS inspection was unavailable: {error}")


def main() -> None:
    st.set_page_config(
        page_title="Cloud VM Optimizer",
        page_icon="☁️",
        layout="wide",
    )
    st.title("Cloud Resource Usage Forecasting and VM Optimization Dashboard")
    st.caption(
        "A college demonstration of XGBoost forecasting and dual-objective "
        "Particle Swarm Optimization (PSO)."
    )

    with st.sidebar:
        st.header("Demo controls")
        st.selectbox("Built-in dataset", ["Synthetic hourly cloud workload"])
        horizon = st.slider("Forecast horizon (hours)", 1, 24, 6)
        current_vms = st.number_input("Current VM count", min_value=1, max_value=50, value=4)
        cost_weight = st.slider("Cost objective weight", 0.0, 1.0, 0.5, 0.05)
        energy_weight = 1.0 - cost_weight
        st.caption(f"Energy objective weight: {energy_weight:.2f}")
        st.info("Demo pricing assumptions are fictional and are not current AWS prices.")

    history = load_workload()
    catalog = load_vm_catalog()

    st.header("1. Project Overview")
    st.write(
        "Historical CPU, RAM, and job counts are converted into lag features. "
        "XGBoost forecasts future demand, then a baseline allocator and PSO choose VM capacity."
    )
    with st.expander("What do XGBoost and PSO do?"):
        st.write(
            "XGBoost learns non-linear workload patterns from historical examples. "
            "PSO treats each possible VM mix as a particle and moves candidate solutions "
            "toward their personal best and the swarm's global best allocation."
        )

    st.header("2. Historical Resource Usage")
    recent = history.tail(7 * 24).set_index("timestamp")
    usage_tab, jobs_tab, data_tab = st.tabs(["CPU and RAM", "Jobs", "Data"])
    with usage_tab:
        st.line_chart(recent[["cpu_usage", "ram_usage"]])
    with jobs_tab:
        st.line_chart(recent[["job_count"]])
    with data_tab:
        st.dataframe(history.tail(48), width="stretch", hide_index=True)

    st.header("3. Forecast Resource Demand")
    if st.button("Run Forecast", type="primary", width="stretch"):
        with st.spinner("Training XGBoost on a chronological train/test split..."):
            st.session_state.forecast_result = run_forecast(history, horizon_hours=horizon)
            st.session_state.forecast_horizon = horizon
            st.session_state.pop("optimization_result", None)
            st.session_state.pop("optimization_controls", None)

    forecast = st.session_state.get("forecast_result")
    if forecast is not None and st.session_state.get("forecast_horizon") != horizon:
        st.info("The forecast horizon changed. Click Run Forecast to refresh the results.")
        forecast = None
    if forecast is None:
        st.info("Choose a horizon and click Run Forecast to begin.")
    else:
        forecast_frame = forecast_result_to_frame(forecast)
        peak_cpu = forecast_frame["cpu_usage"].max()
        peak_ram = forecast_frame["ram_usage"].max()
        peak_jobs = forecast_frame["job_count"].max()
        metric_columns = st.columns(4)
        metric_columns[0].metric("Peak predicted CPU", f"{peak_cpu:.1f}%")
        metric_columns[1].metric("Peak predicted RAM", f"{peak_ram:.1f}%")
        metric_columns[2].metric("Peak predicted jobs", f"{peak_jobs:.0f}")
        metric_columns[3].metric("Forecast horizon", f"{len(forecast.points)} hours")
        st.line_chart(forecast_frame.set_index("timestamp"))

        st.subheader("Actual hold-out accuracy")
        st.caption(
            f"Metrics use {forecast.test_rows} unseen chronological rows after training "
            f"on {forecast.train_rows} rows; they are not manually entered."
        )
        accuracy = pd.DataFrame(
            [
                {"Signal": name, "MAE": score.mae, "RMSE": score.rmse}
                for name, score in forecast.metrics.items()
            ]
        )
        st.dataframe(accuracy.style.format({"MAE": "{:.3f}", "RMSE": "{:.3f}"}), hide_index=True)
        with st.expander("What are MAE and RMSE?"):
            st.write(
                "MAE is the average absolute prediction error. RMSE squares errors before "
                "averaging, so it gives extra importance to larger misses. Lower is better."
            )

    st.header("4. VM Allocation")
    optimize_clicked = st.button(
        "Optimize VM Allocation",
        disabled=forecast is None,
        width="stretch",
    )
    if optimize_clicked and forecast is not None:
        with st.spinner("Comparing the baseline with the PSO swarm..."):
            st.session_state.optimization_result = optimize_forecast(
                forecast,
                catalog,
                current_vms=int(current_vms),
                cost_weight=cost_weight,
                energy_weight=energy_weight,
            )
            st.session_state.optimization_controls = (
                int(current_vms),
                float(cost_weight),
                float(energy_weight),
            )

    comparison = st.session_state.get("optimization_result")
    current_controls = (int(current_vms), float(cost_weight), float(energy_weight))
    if comparison is not None and st.session_state.get("optimization_controls") != current_controls:
        st.info("Allocation controls changed. Click Optimize VM Allocation to refresh the comparison.")
        comparison = None
    if comparison is None:
        st.info("Run the forecast, then click Optimize VM Allocation.")
    else:
        baseline_column, optimized_column = st.columns(2)
        with baseline_column:
            st.subheader("Baseline Allocation")
            st.dataframe(_allocation_table(comparison.baseline), hide_index=True, width="stretch")
        with optimized_column:
            st.subheader("PSO Optimized Allocation")
            st.dataframe(_allocation_table(comparison.optimized), hide_index=True, width="stretch")

        st.header("5. Cost Comparison")
        st.bar_chart(
            pd.DataFrame(
                {
                    "Method": ["Baseline", "PSO"],
                    "Cost (USD)": [comparison.baseline.cost_usd, comparison.optimized.cost_usd],
                }
            ).set_index("Method")
        )
        st.metric("Estimated cost improvement", f"{comparison.cost_improvement_percent:.1f}%")

        st.header("6. Energy Comparison")
        st.bar_chart(
            pd.DataFrame(
                {
                    "Method": ["Baseline", "PSO"],
                    "Energy (kWh)": [
                        comparison.baseline.energy_kwh,
                        comparison.optimized.energy_kwh,
                    ],
                }
            ).set_index("Method")
        )
        st.metric("Estimated energy improvement", f"{comparison.energy_improvement_percent:.1f}%")
        st.caption(
            "Energy is a transparent simulation based on catalog watts, utilization, and time. "
            "It is not exact physical-server energy reported by AWS."
        )

        st.header("7. Scaling Recommendation")
        recommendation = comparison.recommendation
        if recommendation.action == "SCALE UP":
            st.warning(recommendation.message)
        elif recommendation.action == "SCALE DOWN":
            st.success(recommendation.message)
        else:
            st.info(recommendation.message)
        st.write(
            f"Current VMs: **{int(current_vms)}** · Recommended VMs: "
            f"**{comparison.optimized.total_vms}**"
        )
        with st.expander("What is the optimization objective?"):
            st.write(
                f"Objective = {cost_weight:.2f} × normalized cost + "
                f"{energy_weight:.2f} × normalized energy. CPU, RAM, and job capacity "
                "must all meet the peak forecast demand."
            )

    _show_aws_demo()
    st.divider()
    st.caption("Milestone A · Safe demo mode · No automatic EC2 creation or scaling")


if __name__ == "__main__":
    main()
