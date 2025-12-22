#!/bin/bash

export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7
MODEL_LIST=("reasonv/phi4_full_sft.yaml")
DATASET_LIST=("deepscaler-phi4-min" "deepscaler-phi4-rand")
# MODEL_LIST=("reasonv/deepseek_distill_llama8B_full_sft.yaml" "reasonv/deepseek_distill_qwen7B_full_sft.yaml" "reasonv/deepseek_distill_qwen1.5B_full_sft.yaml")
# DATASET_LIST=("deepscaler-14b-min-all" "deepscaler-14b-rand-all")

for DATASET in "${DATASET_LIST[@]}"; do
    for MODEL_CONFIG in "${MODEL_LIST[@]}"; do
        MODEL_NAME=$(basename "$MODEL_CONFIG" _full_sft.yaml)

        case "$MODEL_NAME" in
            deepseek_distill_qwen1.5B)
                LR_LIST=("5e-5")
                ;;
            deepseek_distill_llama8B)
                LR_LIST=("5e-6")
                ;;
            deepseek_distill_qwen7B)
                LR_LIST=("1e-5")
                ;;
            phi4)
                LR_LIST=("8e-6")
                ;;
            *)
                echo "⚠️ Unknown $MODEL_NAME，Skipping"
                continue
                ;;
        esac

        for LR in "${LR_LIST[@]}"; do
            TEMP_CONFIG="temp_config_${MODEL_NAME}_${DATASET}_lr${LR}.yaml"
            cp "$MODEL_CONFIG" "$TEMP_CONFIG"

            sed -i "s|^dataset: .*|dataset: ${DATASET}|" "$TEMP_CONFIG"
            sed -i "s|^learning_rate: .*|learning_rate: ${LR}|" "$TEMP_CONFIG"

            echo "🔁 Running with model=$MODEL_NAME dataset=$DATASET lr=$LR"
            llamafactory-cli train "$TEMP_CONFIG"
        done
    done
done

echo "✅ All training runs completed. Launching single_math.py ..."
